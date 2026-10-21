import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_network import validate

class NetworkTests(unittest.TestCase):
    def setUp(self):
        self.data = dict(vpc_cidr="10.0.0.0/16", azs=["us-east-1a", "us-east-1b"],
                        public_subnet_cidrs=["10.0.1.0/24", "10.0.2.0/24"],
                        private_subnet_cidrs=["10.0.3.0/24", "10.0.4.0/24"])
    def test_valid(self):
        self.assertEqual(validate(self.data), [])
    def test_overlap(self):
        self.data["private_subnet_cidrs"] = ["10.0.1.0/24"]
        self.assertIn("Overlapping subnets", validate(self.data))
    def test_outside(self):
        self.data["private_subnet_cidrs"] = ["192.168.1.0/24"]
        self.assertIn("Subnet outside VPC", validate(self.data))
    def test_zone_count(self):
        self.data["azs"] = ["us-east-1a"]
        self.assertIn("Subnet count exceeds zone count", validate(self.data))
    def test_duplicate_zones(self):
        self.data["azs"] = ["us-east-1a", "us-east-1a"]
        self.assertTrue(validate(self.data))
    def test_host_bits(self):
        self.data["vpc_cidr"] = "10.0.0.1/16"
        self.assertTrue(validate(self.data))
    def test_missing_input(self):
        self.assertTrue(validate({}))
    def test_small_subnet(self):
        self.data["public_subnet_cidrs"] = ["10.0.1.0/29"]
        self.assertIn("Invalid AWS IPv4 subnet prefix", validate(self.data))
