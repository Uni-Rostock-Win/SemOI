import logging
from semanticQuery import views
from django.test import TestCase
from rest_framework.test import APIRequestFactory

# Create your tests here.
class RESTtest(TestCase):
    def setUp(self):
        self.view = views.semanticCall
        self.factory = APIRequestFactory()
    def testSinglePostCall(self):
        request = self.factory.post(self.view, data={"data": ["/m/0hg7b=0.15"]})
        resp = self.view(request)
        logging.info(resp.data)
        print(len(resp.data))
        self.assertGreater(len(resp.data),1)