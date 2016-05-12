from tests.test_actions import *
from ltk.watch import WatchAction
from threading import Thread
import unittest

@unittest.skip("skip testing watch for now")
class TestWatch(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        create_config()

    @classmethod
    def tearDownClass(cls):
        cleanup()

    def setUp(self):
        self.action = WatchAction(os.getcwd())
        self.files = ['sample.txt']
        for fn in self.files:
            create_txt_file(fn)
        self.downloaded = []
        self.action.add_action(None, ['sample*.txt'], force=True)
        self.doc_ids = self.action.doc_manager.get_doc_ids()
        for doc_id in self.doc_ids:
            assert poll_doc(self.action, doc_id)
        # todo current problem: watchdog does not seem to detect changes in daemon
        # but not daemonizing watch causes tests to hang..
        watch_thread = Thread(target=self.action.watch_action, args=(None, (), None, 5,))
        watch_thread.daemon = True
        watch_thread.start()

    def tearDown(self):
        for fn in self.files:
            self.action.rm_action(fn, True)
        self.action.clean_action(False, False, None)
        for fn in self.downloaded:
            os.remove(fn)

    def test_watch_new_file(self):
        file_name = "new_file.txt"
        added_file = create_txt_file(file_name)
        # check if watch detected file and added it to db
        assert self.action.doc_manager.get_doc_by_prop('name', file_name)

    def test_watch_update(self):
        append_file(self.files[0])
        time.sleep(20)
        downloaded_path = self.action.download_action(self.doc_ids[0], None, False)
        self.downloaded.append(downloaded_path)
        with open(downloaded_path, 'r') as f:
            downloaded = f.read()
        assert "Appended text. " in downloaded


# todo make download dir for watch, then just delete folder in teardown or teardownclass
