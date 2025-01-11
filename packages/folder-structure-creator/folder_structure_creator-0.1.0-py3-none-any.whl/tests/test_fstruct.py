import unittest
import os
from folder_structure_creator.fstruct import create_folder_structure_from_file

class TestFolderStructureCreator(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory for the tests."""
        self.test_dir = 'test_folder'
        os.makedirs(self.test_dir, exist_ok=True)
        self.test_file = os.path.join(self.test_dir, 'test_structure.txt')

    def tearDown(self):
        """Clean up the temporary directory after the tests."""
        for root, dirs, files in os.walk(self.test_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.test_dir)

    def test_create_folder_structure_from_file(self):
        """Test creating folders from a text file."""
        # Create a test text file with folder structure
        with open(self.test_file, 'w') as f:
            f.write('ParentFolder\n ChildFolder1\n  SubChildFolder1\n ChildFolder2\n')

        # Call the function to create folders in the test directory
        create_folder_structure_from_file(self.test_file, self.test_dir)

        # Check if the folders were created correctly
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'ParentFolder')))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'ParentFolder', 'ChildFolder1')))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'ParentFolder', 'ChildFolder1', 'SubChildFolder1')))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'ParentFolder', 'ChildFolder2')))

if __name__ == '__main__':
    unittest.main()
