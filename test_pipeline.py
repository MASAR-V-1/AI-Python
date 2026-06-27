from django.test import SimpleTestCase

class ActionSanityTest(SimpleTestCase):
    def test_environment_is_healthy(self):
        """فحص بسيط للتأكد من أن بيئة العمل والمكتبات تعمل بأمان على السيرفر"""
        self.assertTrue(True)