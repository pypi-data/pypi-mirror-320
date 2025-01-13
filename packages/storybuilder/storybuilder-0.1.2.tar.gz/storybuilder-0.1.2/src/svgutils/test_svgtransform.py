import unittest
import xml.etree.ElementTree as ET
from .svgtransform import remove_duplicate_paths, format_path_data

class TestSVGTransform(unittest.TestCase):
    def create_test_svg(self, paths):
        """创建测试用的SVG树"""
        root = ET.Element('svg')
        root.set('xmlns', 'http://www.w3.org/2000/svg')
        
        # 创建一个g元素
        g = ET.SubElement(root, 'g')
        
        # 添加路径
        for d in paths:
            path = ET.SubElement(g, 'path')
            path.set('d', d)
            if isinstance(d, dict):
                for attr, value in d.items():
                    if attr != 'd':
                        path.set(attr, value)
        
        return root

    def count_paths(self, root):
        """计算SVG中的路径数量"""
        return len(root.findall('.//path'))

    def get_path_data(self, root):
        """获取所有路径数据"""
        return [path.get('d') for path in root.findall('.//path')]

    def test_remove_simple_duplicates(self):
        """测试简单的重复路径移除"""
        paths = [
            "M0 0L10 10",
            "M0 0L10 10",  # 完全相同的路径
            "M20 20L30 30"
        ]
        root = self.create_test_svg(paths)
        
        # 移除重复路径前的数量
        self.assertEqual(self.count_paths(root), 3)
        
        remove_duplicate_paths(root)
        
        # 验证结果
        remaining_paths = self.count_paths(root)
        self.assertEqual(remaining_paths, 2)
        
        path_data = self.get_path_data(root)
        self.assertIn("M0 0L10 10", path_data)
        self.assertIn("M20 20L30 30", path_data)

    def test_remove_duplicates_with_different_spacing(self):
        """测试带有不同空格的重复路径移除"""
        paths = [
            "M0 0 L10 10",
            "M0 0L10 10",  # 相同路径，不同空格
            "M0,0,L10,10"  # 相同路径，使用逗号
        ]
        root = self.create_test_svg(paths)
        
        remove_duplicate_paths(root)
        
        # 验证结果
        self.assertEqual(self.count_paths(root), 1)

    def test_preserve_attributes(self):
        """测试在移除重复路径时保留属性"""
        paths = [
            {"d": "M0 0L10 10", "fill": "red"},
            {"d": "M0 0L10 10", "fill": "blue"},  # 相同路径，不同属性
        ]
        root = self.create_test_svg(paths)
        
        remove_duplicate_paths(root)
        
        # 验证结果
        remaining_paths = root.findall('.//path')
        self.assertEqual(len(remaining_paths), 1)
        # 应该保留最后一个路径的属性
        self.assertEqual(remaining_paths[0].get('fill'), 'blue')

    def test_nested_groups(self):
        """测试嵌套组中的重复路径移除"""
        # 创建更复杂的SVG结构
        root = ET.Element('svg')
        g1 = ET.SubElement(root, 'g')
        g2 = ET.SubElement(root, 'g')
        g3 = ET.SubElement(g1, 'g')
        
        # 在不同组中添加相同的路径
        path1 = ET.SubElement(g1, 'path')
        path1.set('d', 'M0 0L10 10')
        
        path2 = ET.SubElement(g2, 'path')
        path2.set('d', 'M0 0L10 10')
        
        path3 = ET.SubElement(g3, 'path')
        path3.set('d', 'M0 0L10 10')
        
        remove_duplicate_paths(root)
        
        # 验证结果
        self.assertEqual(self.count_paths(root), 1)

    def test_format_path_data(self):
        """测试路径数据格式化"""
        test_cases = [
            (
                "M 0 0 L 10 10",
                "M0 0L10 10"
            ),
            (
                "M 0,0 L 10,10",
                "M0 0L10 10"
            ),
            (
                "M  0  0  L  10  10  Z",
                "M0 0L10 10Z"
            ),
        ]
        
        for input_data, expected in test_cases:
            result = format_path_data(input_data)
            self.assertEqual(
                result, 
                expected,
                f"Format path data failed for '{input_data}'\nExpected: '{expected}'\nGot: '{result}'"
            )

if __name__ == '__main__':
    unittest.main() 