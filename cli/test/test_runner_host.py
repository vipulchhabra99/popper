import os
import unittest


from popper.parser import YMLWorkflow
from popper.runner import WorkflowRunner
from popper.cli import log as log
from popper_test import PopperTest


class TestHostRunner(unittest.TestCase, PopperTest):
    def setUp(self):
        log.setLevel('CRITICAL')

    def test_run(self):
        repo = self.mk_repo()

        with WorkflowRunner(workspace_dir=repo.working_dir) as r:
            wf = YMLWorkflow("""
            version: '1'
            steps:
            - uses: sh
              runs: [cat]
              args: README.md
            """)
            wf.parse()
            r.run(wf)

            wf = YMLWorkflow("""
            version: '1'
            steps:
            - uses: 'sh'
              runs: ['bash', '-c', 'echo $FOO > hello.txt ; pwd']
              env: {
                  FOO: bar
              }
            """)
            wf.parse()
            r.run(wf)
            with open(os.path.join(repo.working_dir, 'hello.txt'), 'r') as f:
                self.assertEqual(f.read(), 'bar\n')

            wf = YMLWorkflow("""
            version: '1'
            steps:
            - uses: 'sh'
              runs: 'nocommandisnamedlikethis'
            """)
            wf.parse()
            self.assertRaises(SystemExit, r.run, wf)

        repo.close()
