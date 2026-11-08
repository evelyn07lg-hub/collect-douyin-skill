import importlib.util,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('collect_skill_entry',ROOT/'scripts/collect.py')
entry=importlib.util.module_from_spec(spec);spec.loader.exec_module(entry)
from douyin_viral_collector.browser_choice import browser_options

class SkillEntryTests(unittest.TestCase):
    def test_root_skill_and_no_desktop_dependencies(self):
        text=(ROOT/'SKILL.md').read_text(encoding='utf-8-sig')
        self.assertTrue(text.startswith('---\nname: collect-douyin-skill'))
        self.assertFalse((ROOT/'scripts/desktop.py').exists())
        self.assertFalse((ROOT/'src/douyin_viral_collector/desktop_runner.py').exists())
    def test_browser_channels_are_same_on_all_platforms(self):
        for platform in ('win32','darwin','linux'):
            with patch.object(sys,'platform',platform):
                self.assertEqual(browser_options({},'data')[1],'chromium')
                self.assertEqual(browser_options({'browser':'edge'},'data')[1],'msedge')
                self.assertEqual(browser_options({'browser':'chrome'},'data')[1],'chrome')
        self.assertEqual(len({browser_options({'browser':b},'data')[0] for b in ('edge','chrome','chromium')}),3)
    def test_complete_environment_does_not_install(self):
        with patch('douyin_viral_collector.environment_setup.choose_runtime',return_value=(Path(sys.executable),[])),patch.object(entry.subprocess,'run') as run:
            result=entry.bootstrap(['--features','core'])
        self.assertTrue(result['prepared']);run.assert_not_called()
    def test_setup_strict_multiple_accounts_and_separate_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            w=Path(tmp);result=entry.setup(w,['--profile','https://www.douyin.com/user/demo1','--profile','https://www.douyin.com/user/demo2','--min-likes','30','--strict','--browser','chrome'])
            config=json.loads((w/'config.json').read_text(encoding='utf-8'))
            self.assertEqual(len(config['public_profiles']),2);self.assertEqual(config['threshold'],30);self.assertNotIn('minimum_likes',config)
            self.assertEqual(config['browser'],'chrome');self.assertFalse(config['wps']['enabled']);self.assertTrue(Path(config['model']).is_absolute())
    def test_configure_validation_preserves_prior_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            w=Path(tmp);entry.setup(w,['--profile','https://www.douyin.com/user/demo','--min-likes','30']);original=(w/'config.json').read_bytes()
            for patch_value in ({'unsupported':1},{'document_format':{'body_size':-1}},{'wps':{'enabled':True}}):
                file=w/'settings.json';file.write_text(json.dumps(patch_value),encoding='utf-8')
                with self.assertRaises(ValueError):entry.configure(w,['--settings',str(file)])
                self.assertEqual((w/'config.json').read_bytes(),original)
    def test_reference_and_format_merge(self):
        with tempfile.TemporaryDirectory() as tmp:
            w=Path(tmp);entry.setup(w,['--profile','https://www.douyin.com/user/demo']);(w/'reference.txt').write_text('用户确认的参考文字。',encoding='utf-8')
            file=w/'settings.json';file.write_text(json.dumps({'document_format':{'font':'Arial','body_size':12},'proofreading':{'reference_path':'reference.txt'}}),encoding='utf-8');entry.configure(w,['--settings',str(file)])
            result=json.loads((w/'config.json').read_text(encoding='utf-8'));self.assertTrue(result['proofreading']['enabled']);self.assertEqual(result['document_format']['body_size'],12);self.assertTrue(Path(result['proofreading']['reference_path']).is_absolute())
            self.assertTrue(list(w.glob('config.json.backup-*')))
    def test_script_to_real_docx_without_editor(self):
        with tempfile.TemporaryDirectory() as tmp:
            w=Path(tmp);entry.setup(w,['--profile','https://www.douyin.com/user/demo','--min-likes','30'])
            file=w/'records.json';file.write_text(json.dumps([{'account_id':'demo','account_name':'示例作者','id':'example','likes':31,'published_at':'2026-01-01','body':'这是一段用于验证的完整正文。','title':'示例'}],ensure_ascii=False),encoding='utf-8')
            run=subprocess.run([sys.executable,str(ROOT/'scripts/collect.py'),'--workspace',str(w),'export-word','--input',str(file)],capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(run.returncode,0,run.stderr+run.stdout);result=json.loads(run.stdout);self.assertEqual(result['result']['count'],1)
            self.assertTrue(Path(result['result']['path']).is_file())
