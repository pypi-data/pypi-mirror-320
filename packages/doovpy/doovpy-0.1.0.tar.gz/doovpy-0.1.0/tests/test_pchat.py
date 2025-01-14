import unittest
from doovpy.pchat import greet

class TestGreet(unittest.TestCase):
	def test_greet(self):
		self.assertEqual(greet(),"Hey doov it's peeg")

if __name__=="__main__":
	unittest.main()
