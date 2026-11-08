"""Headless controller for assistants; browser login stays visible and user-owned."""
import argparse,copy,json,os,subprocess,sys,platform,venv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))


def emit(value):
    print(json.dumps(value,ensure_ascii=False),flush=True)


def bootstrap(args):
    from douyin_viral_collector.environment_setup import choose_runtime,probe,requirements,existing_model
    p=argparse.ArgumentParser();p.add_argument('--features',nargs='+',choices=['core','browser','media','proofreading'],default=['core','browser','media','proofreading']);p.add_argument('--models',action='store_true');p.add_argument('--model',choices=['small','large-v3-turbo'],default='small');p.add_argument('--browser',choices=['chromium','chrome','edge'],default='chromium');p.add_argument('--dry-run',action='store_true');a=p.parse_args(args)
    needed=requirements({},features=a.features);python,missing=choose_runtime(ROOT,sys.executable,needed)
    if a.dry_run:return {'python':str(python),'missing':missing,'will_download_models':a.models,'browser':a.browser}
    if missing:
        if not python.is_file():venv.EnvBuilder(with_pip=True,system_site_packages=True).create(ROOT/'.venv')
        report=probe(python,needed);missing=report['missing'] if report else needed
        if missing:subprocess.run([str(python),'-m','pip','install',*missing],check=True)
        report=probe(python,needed)
        if report is None or report['missing']:raise RuntimeError('Environment preparation incomplete')
    if 'browser' in a.features and a.browser=='chromium':
        subprocess.run([str(python),'-m','playwright','install','chromium'],check=True)
    if a.models:
        if existing_model(ROOT,python,a.model) is None:subprocess.run([str(python),str(ROOT/'scripts/download-model.py'),'--model',a.model],check=True,cwd=ROOT)
        from douyin_viral_collector.quality_setup import punctuation_model
        if 'proofreading' in a.features and punctuation_model(ROOT,python) is None:subprocess.run([str(python),str(ROOT/'scripts/download-punctuation.py')],check=True,cwd=ROOT)
    return {'python':str(python),'root':str(ROOT),'prepared':True,'models_requested':a.models,'browser':a.browser,'next':'Use this Python executable for subsequent collect.py commands.'}


def capabilities():
    from douyin_viral_collector.environment_setup import choose_runtime,requirements
    python,missing=choose_runtime(ROOT,sys.executable,requirements({'proofreading':{'enabled':True}}))
    return {'skill':'collect-douyin-skill','version':'1.0.0','platform':platform.system(),'architecture':platform.machine(),'python':str(python),'missing_dependencies':missing,'display_available':sys.platform in ('win32','darwin') or bool(os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY')),'requires':['Python 3.10+ (3.12 recommended)','browser display and user login for live collection','filesystem and subprocess access'],'desktop_workbench':False,'cloud_enabled_by_default':False}


def configure(workspace,args):
    from douyin_viral_collector.document_settings import save_settings,formatting
    p=argparse.ArgumentParser();p.add_argument('--settings',required=True);a=p.parse_args(args)
    patch=json.loads(Path(a.settings).read_text(encoding='utf-8-sig'));path=workspace/'config.json'
    if not isinstance(patch,dict):raise ValueError('settings must be a JSON object')
    allowed={'browser','document_format','word_export','wps','proofreading','collection','browser_budgets','caption_only_work_ids'}
    if set(patch)-allowed:raise ValueError('Unsupported configuration fields: '+', '.join(sorted(set(patch)-allowed)))
    original=json.loads(path.read_text(encoding='utf-8-sig'));values=copy.deepcopy(original)
    def merge(target,source):
        for key,value in source.items():
            if isinstance(value,dict):
                if not isinstance(target.get(key),dict):target[key]={}
                merge(target[key],value)
            else:target[key]=value
    merge(values,patch)
    if values.get('browser') not in ('edge','chrome','chromium'):raise ValueError('Invalid browser')
    formatting(values)
    for key in ('reference_path',):
        ref=values.get('proofreading',{}).get(key)
        if ref:
            resolved=(workspace/ref).resolve()
            if not resolved.is_file() or resolved.suffix.lower() not in ('.txt','.md','.docx'):raise ValueError('Reference file is missing or unsupported')
            values['proofreading'][key]=str(resolved)
    base=values.get('word_export',{}).get('base_document')
    if base:
        base=(workspace/base).resolve()
        if not base.is_file() or base.suffix.lower()!='.docx':raise ValueError('Existing document must be a .docx file')
        values['word_export']['base_document']=str(base)
    cloud=values.get('wps',{})
    if cloud.get('enabled'):
        from douyin_viral_collector.wps_browser import configured_wps_target
        configured_wps_target(values)
    import time,shutil
    shutil.copy2(path,path.with_name('config.json.backup-'+str(time.time_ns())))
    pending=path.with_suffix('.json.tmp');pending.write_text(json.dumps(values,ensure_ascii=False,indent=2),encoding='utf-8');pending.replace(path)
    return {'configured':True,'workspace':str(workspace),'cloud_enabled':bool(cloud.get('enabled'))}


def setup(workspace,args):
    from douyin_viral_collector.onboarding import setup as create
    p=argparse.ArgumentParser();p.add_argument('--profile',action='append',required=True);p.add_argument('--min-likes',type=int,default=500);p.add_argument('--strict',action='store_true');p.add_argument('--browser',choices=['chromium','edge','chrome']);p.add_argument('--output-dir');a=p.parse_args(args)
    path=workspace/'config.json'
    # Persist the browser choice before resolving copied short links.
    if not path.exists():path.write_text((ROOT/'config.example.json').read_text(encoding='utf-8-sig'),encoding='utf-8')
    if a.browser:
        d=json.loads(path.read_text(encoding='utf-8-sig'));d['browser']=a.browser;path.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
    result=create(str(path),a.profile,a.min_likes,a.strict,a.output_dir)
    d=json.loads(path.read_text(encoding='utf-8-sig'))
    for group,key in [('','model'),('proofreading','punctuation_model')]:
        target=d[group] if group else d;value=Path(target[key]);target[key]=str(value if value.is_absolute() else ROOT/value)
    path.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');return result


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--workspace',default=str(Path.home()/'.collect-douyin'));p.add_argument('command',help='capabilities, bootstrap, setup, configure, login, organize, status, videos, export-word, or another collection command');p.add_argument('arguments',nargs=argparse.REMAINDER);a=p.parse_args(argv)
    workspace=Path(a.workspace).expanduser().resolve()
    if a.command=='capabilities':return capabilities()
    if a.command=='bootstrap':return bootstrap(a.arguments)
    workspace.mkdir(parents=True,exist_ok=True)
    if a.command=='setup':return setup(workspace,a.arguments)
    if a.command=='configure':return configure(workspace,a.arguments)
    config=workspace/'config.json'
    if not config.is_file():raise ValueError('Run setup first; account homepage links are required')
    env=dict(os.environ,PYTHONPATH=str(ROOT/'src'),PYTHONIOENCODING='utf-8')
    subprocess.run([sys.executable,'-m','douyin_viral_collector.cli','--config',str(config),a.command,*a.arguments],env=env,cwd=ROOT,check=True)
    return None

if __name__=='__main__':
    try:
        result=main()
        if result is not None:emit({'ok':True,'result':result})
    except (ValueError,RuntimeError,OSError) as exc:
        emit({'ok':False,'error':str(exc)});raise SystemExit(1)
    except subprocess.CalledProcessError as exc:
        raise SystemExit(exc.returncode)
