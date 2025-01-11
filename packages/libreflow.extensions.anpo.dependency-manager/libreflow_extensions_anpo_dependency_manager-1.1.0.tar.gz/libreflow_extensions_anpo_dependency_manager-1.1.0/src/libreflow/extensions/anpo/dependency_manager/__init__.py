import re
import os
from os.path import exists
from pprint import pprint
from re import match, search
from blender_asset_tracer import trace
from pathlib import Path
from kabaret import flow
from kabaret.flow.object import _Manager
from kabaret.flow_contextual_dict import get_contextual_dict
from kabaret.app.ui.gui.icons import gui as _
from libreflow.baseflow.file import TrackedFile, TrackedFolder, Revision
from libreflow.resources.icons import libreflow as _
from libreflow.resources.icons import gui as _

from . import _version
__version__ = _version.get_versions()['version']

               # entity type    entity name          dep name      path filter
PATH_FILTERS = [('asset',       '{asset}',           'rig',        r"^/lib/(?P<asset_type>(characters|props|animals))/(?P<asset_family>[^/]+)/(?P<asset>[^/]+)/(?P<task>rigging)/(?P<file>rigging_blend)/(?P<revision>v\d{3})/(?P<file_name>[^/]+_rigging\.blend)$"),
                ('asset',       '{asset}',           'textures',   r"^/lib/(?P<asset_type>(characters|props|animals))/(?P<asset_family>[^/]+)/(?P<asset>[^/]+)/(?P<task>shading)/(?P<file>textures(_\dk)?)/(?P<revision>v\d{3})/(?P<file_name>[^/]+)$"),
                ('asset',       '{asset}',           'set_layers', r"^/lib/(?P<asset_type>sets)/(?P<asset_family>sq\d{3}[A-Za-z]?)/(?P<asset>sq\d{3}[A-Za-z]?[-_]bg\d{5})/(?P<task>design)/(?P<file>layers)/(?P<revision>v\d{3})/(?P<file_name>[^/]+)$"),
                ('shot',        '{sequence}_{shot}', 'animatic',   r"^/anpo/(?P<sequence>sq\d{3}[A-Za-z]?)/(?P<shot>sh\d{5})/(?P<task>layout)/(?P<file>animatic_mov)/(?P<revision>v\d{3})/(?P<file_name>sq\d{3}[A-Za-z]?_sh\d{5}_animatic\.mov)$"),
                ('shot',        '{sequence}_{shot}', 'ref_layout', r"^/anpo/(?P<sequence>sq\d{3}[A-Za-z]?)/(?P<shot>sh\d{5})/(?P<task>animblock)/(?P<file>ref_layout_abc)/(?P<revision>v\d{3})/(?P<file_name>sq\d{3}[A-Za-z]?_sh\d{5}_ref_layout\.abc)$")]

def make_shot_oid(matches):
    return "/anpo/films/anpo/sequences/{sequence}/shots/{shot}/tasks/{task}/files/{file}/history/revisions/{revision}".format(**matches)

def make_asset_oid(matches):
    matches['asset'] = matches['asset'].replace('-', '_') # handle '-' in asset variation name
    return "/anpo/asset_types/{asset_type}/asset_families/{asset_family}/assets/{asset}/tasks/{task}/files/{file}/history/revisions/{revision}".format(**matches)

MAKE_OID_FUNCS = {'asset': make_asset_oid,
                  'shot': make_shot_oid}

def add_tracked_dependency(deps, entity_name, name, revision):
    dep_name = f"{entity_name}_{name}_{revision.name()}"
    if dep_name in deps:
        # Skip duplicates
        return
    
    print(f"- found {entity_name} {name} {revision.name()}")
    deps[dep_name] = dict(revision=revision,
                          revision_name=revision.name(),
                          entity_name=entity_name,
                          type_name=name,
                          available=revision.get_sync_status() == 'Available',
                          downloadable=revision.get_sync_status(exchange=True) == 'Available')

def find_revision(root, path, regex, entity_name_format, dep_name, make_oid_func, tracked_deps):
    """
    Check if the given path corresponds to an existing revision
    and add an entry to the `tracked_deps` list of dependencies.
    
    :param root: project root
    :param path: dependency path
    :param regex: regular expression pattern used for matching the dependency path
    :param entity_name_format: pattern used as the entity name in the UI, evaluated with matched keywords
    :param dep_name: dependency nice name
    :param make_oid_func: function returning the revision oid from a dict of keywords (see `make_shot_oid` and `make_asset_oid`)
    :param tracked_deps: updated dict of dependencies
    :return: boolean indicating if a revision has been found
    """
    # Do match
    m = match(regex, path)
    if m is None:
        return False

    # Check for a valid revision
    oid = make_oid_func(m.groupdict())
    try:
        rev = root.get_object(oid)
    except Exception as e:
        return False

    # Add revision to tracked list
    entity_name = entity_name_format.format(**m.groupdict()).replace('-','_')
    add_tracked_dependency(tracked_deps, entity_name, dep_name, rev)
    return True


class DownloadAECompDependencies(flow.Action):

    ICON = ('icons.gui', 'ref')

    _file = flow.Parent()
    _files = flow.Parent(2)
    _task = flow.Parent(3)
    _tasks = flow.Parent(4)

    def allow_context(self, context):
        rev = self._file.get_head_revision()
        return rev is not None

    def needs_dialog(self):
        return False

    def find_dependencies(self):
        self.download_list = []
        root_folder = self.root().project().get_root()

        # Latest animatic revision
        self.session.log_info(' [Download Comp Deps]  - Animatic')
        if self._tasks.has_mapped_name('layout'):
            layout_task = self._tasks['layout']

            animatic = layout_task.files.has_file('animatic', 'mov')
            if animatic is False:
                self.session.log_error('[Download Comp Deps]      - Don\'t exist')
                return False
            else:
                animatic = layout_task.files['animatic_mov']
                animatic_rev = animatic.get_head_revision()
                rev_path = os.path.join(root_folder, animatic_rev.path.get())
                if animatic_rev.get_sync_status() == 'Available' and os.path.exists(rev_path):
                    self.session.log_info(' [Download Comp Deps]      - Up to date')
                else:
                    self.session.log_info(' [Download Comp Deps]      - Not downloaded')
                    self.download_list.append(animatic_rev)
                
                # Create a link
                if self._task.has_file_ref(animatic.oid()) is False:
                    self.session.log_info(' [Download Comp Deps]      - Reference link created')
                    self._task.file_refs.add_ref(animatic.oid(), 'Inputs')

        # Latest After Effects revision
        self.session.log_info(' [Download Comp Deps]  - AE file')
        ae_rev = self._file.get_head_revision()
        rev_path = os.path.join(root_folder, ae_rev.path.get())
        if ae_rev.get_sync_status() == 'Available' and os.path.exists(rev_path):
            self.session.log_info(' [Download Comp Deps]      - Up to date')
        else:
            self.session.log_info(' [Download Comp Deps]      - Not downloaded')
            self.download_list.append(ae_rev)

        # Latest passes folder
        self.session.log_info(' [Download Comp Deps]  - Passes folder')
        passes = self._files.has_folder('passes')
        if passes is False:
            self.session.log_error('[Download Comp Deps]      - Don\'t exist')
            return False
        else:
            passes = self._files['passes']
            passes_rev = passes.get_head_revision()
            rev_path = os.path.join(root_folder, passes_rev.path.get())
            if passes_rev.get_sync_status() == 'Available' and os.path.exists(rev_path):
                self.session.log_info(' [Download Comp Deps]      - Up to date')
            else:
                self.session.log_info(' [Download Comp Deps]      - Not downloaded')
                self.download_list.append(passes_rev)
        
        # Sets files
        shot_number = re.search(r'\d+', self.context_dict["shot"]).group(0)

        sets_family = self.root().get_object('/anpo/asset_types/sets')
        if sets_family.asset_families.has_mapped_name(self.context_dict["sequence"]):
            sets_sequence = sets_family.asset_families[self.context_dict["sequence"]]
            set_name = f'{self.context_dict["sequence"]}_bg{shot_number}'
            
            if sets_sequence.assets.has_mapped_name(set_name):
                sets_shot = sets_sequence.assets[set_name]
                
                if sets_shot.tasks.has_mapped_name('design'):
                    sets_task = sets_shot.tasks['design']

                    # Latest Adobe Illustrator revision
                    self.session.log_info(' [Download Comp Deps]  - AI file')
                    ai_file = sets_task.files.has_file('design', 'ai')
                    if ai_file is False:
                        self.session.log_error('[Download Comp Deps]      - Don\'t exist')
                        
                        return False
                    else:
                        ai_file = sets_task.files['design_ai']
                        ai_rev = ai_file.get_head_revision()
                        rev_path = os.path.join(root_folder, ai_rev.path.get())
                        if ai_rev.get_sync_status() == 'Available' and os.path.exists(rev_path):
                            self.session.log_info(' [Download Comp Deps]      - Up to date')
                        else:
                            self.session.log_info(' [Download Comp Deps]      - Not downloaded')
                            self.download_list.append(ai_rev)

                    # Latest Illustrator layers folder
                    self.session.log_info(' [Download Comp Deps]  - AI layers folder')
                    ai_layers = sets_task.files.has_folder('layers')
                    if ai_layers is False:
                        self.session.log_error('[Download Comp Deps]      - Don\'t exist')
                        return False
                    else:
                        ai_layers = sets_task.files['layers']
                        ai_layers_rev = ai_layers.get_head_revision()
                        rev_path = os.path.join(root_folder, ai_layers_rev.path.get())
                        if ai_layers_rev.get_sync_status() == 'Available' and os.path.exists(rev_path):
                            self.session.log_info(' [Download Comp Deps]      - Up to date')
                        else:
                            self.session.log_info(' [Download Comp Deps]      - Not downloaded')
                            self.download_list.append(ai_layers_rev)
                else:
                    self.session.log_error(f'[Download Comp Deps]  - sets {set_name} design task has not been found')
                    return False
            else:
                self.session.log_error(f'[Download Comp Deps]  - sets {set_name} has not been found')
                return False
        
        return True

    def process_downloads(self):
        request_status = False

        if len(self.download_list) == 0:
            self.session.log_info(f' [Download Comp Deps] All dependencies are up to date')
            return
        else:
            self.session.log_info(f' [Download Comp Deps] Downloading files')

            for rev in self.download_list:
                exchange_status = rev.get_sync_status(exchange=True)
                # Not yet on the exchange server
                if exchange_status is False:
                    self.do_request(rev)
                    request_status = True
                # Ready to download
                else:
                    self.do_download(rev)
        
        return request_status

    def do_download(self, rev):
        # print(f"-- download {dep_data['entity_name']} {dep_data['type_name']} {dep_data['revision_name']}")
        rev.download.run('Confirm')

    def do_request(self, rev):
        current_site = self.root().project().get_current_site().name()
        source_site = rev.site.get()
        # print(f"-- request {dep_data['entity_name']} {dep_data['type_name']} {dep_data['revision_name']}")
        # print(current_site, source_site)
        rev.request_as.sites.source_site.set(source_site)
        rev.request_as.sites.target_site.set(current_site)
        rev.request_as.run('Request')

    def run(self, button):
        self.context_dict = get_contextual_dict(self._file, 'settings')

        self.session = self.root().session()
        self.session.log_info(f' [Download Comp Deps] Check files for {self.context_dict["sequence"]} {self.context_dict["shot"]}')

        step_status = self.find_dependencies()
        if step_status is False:
            self.session.log_error('[Download Comp Deps] Process aborted')
            return
        else:
            step_status = self.process_downloads()
            if step_status is True:
                self.session.log_warning(f' [Download Comp Deps] There are some files that need to be uploaded to the exchange server')
                self.session.log_warning(f' [Download Comp Deps] You should be able to "synchronise files" from the homepage in a few minutes (unless your site is using a autosync session)')

            self.session.log_info(f' [Download Comp Deps] All dependencies that have been downloaded')
            for rev in self.download_list:
                rev_context_dict = get_contextual_dict(rev, 'settings')
                self.session.log_info(f' [Download Comp Deps]  - {rev_context_dict["file_display_name"]} {rev_context_dict["revision"]}')
        
        self.session.log_info(' [Download Comp Deps] Process complete')


class DownloadDep(flow.Action):
    ICON = ('icons.libreflow', 'download')
    _dep = flow.Parent()
    _deps = flow.Parent(2)
    _action = flow.Parent(3)

    def needs_dialog(self):
        return False

    def allow_context(self, context):
        dep_data = self._action.get_tracked_dep(self._dep.name())
        return dep_data['downloadable'] and not dep_data['available']

    def run(self, button):
        self._action.do_download(self._dep.name())
        self._deps.touch()


class RequestDep(flow.Action):
    ICON = ('icons.libreflow', 'request')
    _dep = flow.Parent()
    _deps = flow.Parent(2)
    _action = flow.Parent(3)

    def needs_dialog(self):
        return False

    def allow_context(self, context):
        dep_data = self._action.get_tracked_dep(self._dep.name())
        return not dep_data['available'] and not dep_data['downloadable']

    def run(self, button):
        self._action.do_request(self._dep.name())
        self._deps.touch()


class BlenderDep(flow.SessionObject):
    download = flow.Child(DownloadDep)
    request = flow.Child(RequestDep)
    _deps = flow.Parent()
    
    def get_revision(self):
        return self._deps.get_revision(self.name())


class BlenderDeps(flow.DynamicMap):
    _action = flow.Parent(1)
    _file = flow.Parent(2)

    @classmethod
    def mapped_type(cls):
        return BlenderDep

    def mapped_names(self, page_num=0, page_size=None):
        return sorted(self._action.get_tracked_deps().keys())

    def get_revision(self, dep_name):
        return self._action.get_tracked_dep(dep_name)

    def columns(self):
        return ['Entity', 'Type', 'Revision']

    def summary(self):
        deps = self._action.get_tracked_deps().values()
        unavail = len([d for d in deps \
            if d['revision'].get_sync_status() != 'Available'])
        if unavail > 0:
            return f"<font color=#D66500>{unavail} file(s) not available</font>"
        else:
            return f"<font color=#45CC3D>All files are available !</font>"

    def _fill_row_cells(self, row, item):
        data = self._action.get_tracked_dep(item.name())
        row['Type'] = data['type_name']
        row['Entity'] = data['entity_name']
        row['Revision'] = data['revision_name']
    
    def _fill_row_style(self, style, item, row):
        rev = self._action.get_tracked_dep(item.name())['revision']
        status = rev.get_sync_status()
        if status == 'Available':
            for c in self.columns():
                style[f'{c}_foreground-color'] = '#606060'
            style['icon'] = ('icons.gui', 'checked-white')
            return

        if status == 'Requested':
            icon = 'waiting'
        else:
            status = rev.get_sync_status(exchange=True)
            icon = 'download' if status == 'Available' else 'request'
        style['icon'] = ('icons.libreflow', icon)


class DownloadAll(flow.Action):
    ICON = ('icons.libreflow', 'download')
    _action = flow.Parent()

    def needs_dialog(self):
        return False

    def run(self, button):
        deps = self._action.get_tracked_deps()
        for dep in self._action.tracked_deps.mapped_items():
            dep_data = deps[dep.name()]
            if dep_data['available']:
                continue

            if dep_data['downloadable']:
                self._action.do_download(dep.name())
            else:
                self._action.do_request(dep.name())
        self._action.tracked_deps.touch()


class UntrackedDeps(flow.Object):
    deps = flow.Computed().ui(editor='textarea',
                              html=True)
    _action = flow.Parent()

    def summary(self):
        n = len(self._action.get_untracked_deps())
        return f"<font color=#D66500>{n} untracked file(s) found</font>"

    def compute_child_value(self, child_value):
        if child_value is self.deps:
            paths = [f"<font color=#D5000D>{p} not found</font>" if not exists(p) else p \
                for p in self._action.get_untracked_deps()]
            self.deps.set("<br>".join(paths))

    def _fill_ui(self, ui):
        ui['hidden'] = not bool(self._action.get_untracked_deps())


class CheckBlenderDependencies(flow.Action):
    _MANAGER_TYPE = _Manager
    ICON = ('icons.gui', 'ref')
    tracked_deps = flow.Child(BlenderDeps).ui(expanded=True,
                                              default_height=300,
                                              label='Tracked')
    download_all = flow.Child(DownloadAll)
    untracked_deps = flow.Child(UntrackedDeps).ui(expanded=False,
                                                  label='Untracked')
    _file = flow.Parent()

    def __init__(self, parent, name):
        super(CheckBlenderDependencies, self).__init__(parent, name)
        self._tracked_cache = None
        self._untracked_cache = None

    def allow_context(self, context):
        rev = self.get_revision()
        return rev is not None and rev.get_sync_status() == 'Available'

    def needs_dialog(self):
        settings = get_contextual_dict(self.get_revision(), 'settings')
        self.message.set(f"<h1>{settings['task_display_name']} dependencies - {settings['revision']}</h1>")
        return True

    def get_buttons(self):
        self.untracked_deps.deps.set('\n'.join(self.get_untracked_deps()))
        return ['Update list']

    def get_revision(self):
        """
        Return the Blender file revision to be inspected for
        collecting dependencies.

        The file's head revision is returned by default.
        """
        return self._file.get_head_revision()

    def find_dependencies(self):
        if self._tracked_cache is not None:
            return self._tracked_cache, self._untracked_cache

        start_char = len(self.root().project().get_root().replace('\\', '/'))
        project_name = self.root().project().name()
        bf_path = Path(self.get_revision().get_path())
        self._tracked_cache = dict()
        self._untracked_cache = []

        print(f"Checking dependencies: {bf_path}")
        for dep in trace.deps(bf_path):
            # Match path without project root
            path = str(dep.abspath).replace('\\', '/')[start_char:]
            found = False
            for entity_type_name, entity_name_format, dep_name, regex in PATH_FILTERS:
                found = find_revision(self.root(), path, regex, entity_name_format, dep_name, MAKE_OID_FUNCS[entity_type_name], self._tracked_cache)
                if found:
                    break
            if found:
                continue

            print(f"x unmatched dependency: {path}")
            # Add unmatched dependency to untracked list
            self._untracked_cache.append(str(dep.abspath))

        return self._tracked_cache, self._untracked_cache

    def get_tracked_deps(self):
        self.find_dependencies()
        return self._tracked_cache

    def get_untracked_deps(self):
        self.find_dependencies()
        return self._untracked_cache

    def get_tracked_dep(self, name):
        self.find_dependencies()
        return self._tracked_cache[name]

    def do_download(self, dep_name):
        dep_data = self.get_tracked_dep(dep_name)
        print(f"-- download {dep_data['entity_name']} {dep_data['type_name']} {dep_data['revision_name']}")
        dep_data['revision'].download.run('Confirm')

    def do_request(self, dep_name):
        dep_data = self.get_tracked_dep(dep_name)
        revision = dep_data['revision']
        current_site = self.root().project().get_current_site().name()
        source_site = revision.site.get()
        print(f"-- request {dep_data['entity_name']} {dep_data['type_name']} {dep_data['revision_name']}")
        print(current_site, source_site)
        revision.request_as.sites.source_site.set(source_site)
        revision.request_as.sites.target_site.set(current_site)
        revision.request_as.run('Request')

    def run(self, button):
        if button == 'Update list':
            self._tracked_cache = None
            self._untracked_cache = None
            self.tracked_deps.touch()
            return self.get_result(close=False)


class CheckRevisionDependencies(CheckBlenderDependencies):
    _revision = flow.Parent()
    _file = flow.Parent(3)

    def get_revision(self):
        return self._revision


class CheckLayoutDependencies(CheckBlenderDependencies):
    """
    Action to check the dependencies of the latest
    revision of the layout scene.
    """
    _tasks = flow.Parent(4)

    def get_revision(self):
        if not self._tasks.has_mapped_name('layout'):
            return None

        task = self._tasks['layout']
        if not task.files.has_file('layout', 'blend'):
            return None

        return task.files['layout_blend'].get_head_revision()


class CheckBlockingDependencies(CheckBlenderDependencies):
    """
    Action to check the dependencies of the latest
    revision of the animation blocking scene.
    """
    _tasks = flow.Parent(4)

    def get_revision(self):
        if not self._tasks.has_mapped_name('animblock'):
            return None

        task = self._tasks['animblock']
        if not task.files.has_file('anim_blocking', 'blend'):
            return None

        return task.files['anim_blocking_blend'].get_head_revision()


def check_dependencies(parent):
    if isinstance(parent, TrackedFile) and parent.name().endswith('_blend'):
        cd = flow.Child(CheckBlenderDependencies)
        cd.name = 'check_blender_dependencies'
        cd.index = None
        cd.ui(dialog_size=(900, 700))
        rels = [cd]
        if parent.name() == 'anim_blocking_blend':
            cld = flow.Child(CheckLayoutDependencies)
            cld.name = 'check_layout_dependencies'
            cld.index = None
            cld.ui(dialog_size=(900, 700))
            rels.append(cld)
        elif parent.name() == 'anim_spline_blend':
            cbd = flow.Child(CheckBlockingDependencies)
            cbd.name = 'check_blocking_dependencies'
            cbd.index = None
            cbd.ui(dialog_size=(900, 700))
            rels.append(cbd)
        return rels

    if isinstance(parent, TrackedFile) and parent.name().endswith('_aep') and 'compositing' in parent.oid():
        r = flow.Child(DownloadAECompDependencies)
        r.name = 'download_dependencies'
        r.index = None
        r.ui(dialog_size=(900, 700), label="Download Dependencies")
        return r

    if isinstance(parent, Revision) and parent._file.name().endswith('_blend'):
        r = flow.Child(CheckRevisionDependencies)
        r.name = 'check_dependencies'
        r.index = None
        r.ui(dialog_size=(900, 700))
        return r


def install_extensions(session):
    return {
        "dependency_manager": [
            check_dependencies,
        ]
    }
