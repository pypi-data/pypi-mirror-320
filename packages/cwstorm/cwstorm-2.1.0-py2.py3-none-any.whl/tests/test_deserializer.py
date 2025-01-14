import unittest
from cwstorm.deserializer import deserialize
from cwstorm.dsl.dag_node import DagNode

class TestDeserialization(unittest.TestCase):
    def setUp(self):
        DagNode.reset()
        self.deserialized_data = {
            'nodes': [
                 {'type': 'job', 'name': 'job1'},
                 {'type': 'task', 'name': 'task1', "output_path": "/media/","status": "holding"},
                 {'type': 'upload', 'name': 'upload1',"status": "holding"}
            ],
            'edges': [
                {'source': 'task1', 'target': 'job1'},
                {'source': 'upload1', 'target': 'job1'}
            ]
        }
        
    def tearDown(self):
        DagNode.reset()

    def test_deserialize_connects_nodes(self):
        job = deserialize(self.deserialized_data)
        self.assertEqual(len(job.children), 2)
        self.assertEqual(job.children[0].name(), 'task1')
        self.assertEqual(job.children[1].name(), 'upload1')

if __name__ == '__main__':
    unittest.main()
