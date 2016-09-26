from django.contrib.auth.models import User
from django.test import TestCase
from nextcloudappstore.core.models import App, AppOwnershipTransfer


class AppOwnershipTransferTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1')
        self.user2 = User.objects.create_user(username='user2')
        self.app = App.objects.create(name='App', owner=self.user1)

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()
        self.app.delete()

    def test_transfer(self):
        transfer = AppOwnershipTransfer.objects.create(
            app=self.app, to_user=self.user2)
        self.assertEquals(transfer.from_user, self.user1)
        transfer.commit()
        self.assertEquals(self.app.owner, self.user2)
        self.assertEquals(transfer.id, None)

    def test_transfer_to_self(self):
        with self.assertRaises(RuntimeError):
            AppOwnershipTransfer.objects.create(
                app=self.app, to_user=self.user1)
