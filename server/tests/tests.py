from django.test import TestCase
from django.test import TestCase
from server.views import workflow_list, workflow_addmodule, workflow_detail, module_list, parameterval_detail
from server.views.WfModule import wfmodule_detail,wfmodule_render
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from server.models import ParameterVal, ParameterSpec, Module, WfModule, Workflow
from server.dispatch import test_data_table
from server.tests.utils import *
import pandas as pd
import json

class WorkflowTests(LoggedInTestCase):
    def setUp(self):
        super(WorkflowTests, self).setUp()  # log in
        self.factory = APIRequestFactory()
        add_new_workflow('Workflow 1')
        add_new_workflow('Workflow 2')
        add_new_module('Module 1')
        add_new_module('Module 2')
        add_new_module('Module 3')

    def test_workflow_list_get(self):
        request = self.factory.get('/api/workflows/')
        force_authenticate(request, user=self.user)
        response = workflow_list(request)
        self.assertIs(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], 'Workflow 1')
        self.assertEqual(response.data[1]['name'], 'Workflow 2')

    def test_workflow_list_post(self):
        request = self.factory.post('/api/workflows/', {'name': 'Workflow 3'})
        force_authenticate(request, user=self.user)
        response = workflow_list(request)
        self.assertIs(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Workflow.objects.count(), 3)
        self.assertEqual(Workflow.objects.filter(name='Workflow 3').count(), 1)

    def test_workflow_addmodule_put(self):
        pk_workflow = Workflow.objects.get(name='Workflow 1').id

        request = self.factory.put('/api/workflows/%d/addmodule/' % pk_workflow,
                                   {'moduleID': Module.objects.get(name='Module 1').id,
                                    'insertBefore': 0})
        force_authenticate(request, user=self.user)
        response = workflow_addmodule(request, pk=pk_workflow)
        self.assertIs(response.status_code, status.HTTP_204_NO_CONTENT)

        request = self.factory.put('/api/workflows/%d/addmodule/' % pk_workflow,
                                   {'moduleID': Module.objects.get(name='Module 2').id,
                                    'insertBefore': 0})
        force_authenticate(request, user=self.user)
        response = workflow_addmodule(request, pk=pk_workflow)
        self.assertIs(response.status_code, status.HTTP_204_NO_CONTENT)

        request = self.factory.put('/api/workflows/%d/addmodule/' % pk_workflow,
                                   {'moduleID': Module.objects.get(name='Module 3').id,
                                    'insertBefore': 1})
        force_authenticate(request, user=self.user)
        response = workflow_addmodule(request, pk=pk_workflow)
        self.assertIs(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(list(WfModule.objects.values_list('module', flat=True)),
                         [Module.objects.get(name='Module 2').id,
                          Module.objects.get(name='Module 3').id,
                          Module.objects.get(name='Module 1').id])

        request = self.factory.put('/api/workflows/%d/addmodule/' % 10000,
                                   {'moduleID': Module.objects.get(name='Module 1').id,
                                    'insertBefore': 0})
        force_authenticate(request, user=self.user)
        response = workflow_addmodule(request, pk=10000)
        self.assertIs(response.status_code, status.HTTP_404_NOT_FOUND)

        request = self.factory.put('/api/workflows/%d/addmodule/' % Workflow.objects.get(name='Workflow 1').id,
                                   {'moduleID': 10000,
                                    'insertBefore': 0})
        force_authenticate(request, user=self.user)
        response = workflow_addmodule(request, pk=Workflow.objects.get(name='Workflow 1').id)
        self.assertIs(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_workflow_detail_get(self):
        pk_workflow = Workflow.objects.get(name='Workflow 1').id
        request = self.factory.get('/api/workflows/%d/' % pk_workflow)
        response = workflow_detail(request, pk = pk_workflow)
        self.assertIs(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Workflow 1')

    def test_workflow_detail_get(self):
        pk_workflow = Workflow.objects.get(name='Workflow 1').id
        request = self.factory.get('/api/workflows/%d/' % pk_workflow)
        force_authenticate(request, user=self.user)
        response = workflow_detail(request, pk = pk_workflow)
        self.assertIs(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Workflow 1')

        # bad ID should give 404
        request = self.factory.get('/api/workflows/%d/' % 10000)
        force_authenticate(request, user=self.user)
        response = workflow_detail(request, pk = 10000)
        self.assertIs(response.status_code, status.HTTP_404_NOT_FOUND)

        # not authenticated should give 403
        request = self.factory.get('/api/workflows/%d/' % pk_workflow)
        response = workflow_detail(request, pk=pk_workflow)
        self.assertIs(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_workflow_detail_patch(self):
        pk_workflow = Workflow.objects.get(name='Workflow 1').id

        request = self.factory.put('/api/workflows/%d/addmodule/' % pk_workflow,
                                   {'moduleID': Module.objects.get(name='Module 1').id,
                                    'insertBefore': 0})
        force_authenticate(request, user=self.user)
        response = workflow_addmodule(request, pk=pk_workflow)
        self.assertIs(response.status_code, status.HTTP_204_NO_CONTENT)

        request = self.factory.put('/api/workflows/%d/addmodule/' % pk_workflow,
                                   {'moduleID': Module.objects.get(name='Module 2').id,
                                    'insertBefore': 0})
        force_authenticate(request, user=self.user)
        response = workflow_addmodule(request, pk=pk_workflow)
        self.assertIs(response.status_code, status.HTTP_204_NO_CONTENT)

        request = self.factory.put('/api/workflows/%d/addmodule/' % pk_workflow,
                                   {'moduleID': Module.objects.get(name='Module 3').id,
                                    'insertBefore': 1})
        force_authenticate(request, user=self.user)
        response = workflow_addmodule(request, pk=pk_workflow)
        self.assertIs(response.status_code, status.HTTP_204_NO_CONTENT)

        request = self.factory.patch('/api/workflows/%d/' % pk_workflow, data=[{'id': 1, 'order': 1},
                                                                               {'id': 2, 'order': 2},
                                                                               {'id': 3, 'order': 3}], format='json')
        force_authenticate(request, user=self.user)
        response = workflow_detail(request, pk = pk_workflow)
        self.assertIs(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(list(WfModule.objects.values_list('id', flat=True)), [1, 2, 3])

    def test_workflow_detail_delete(self):
        pk_workflow = Workflow.objects.get(name='Workflow 1').id
        request = self.factory.delete('/api/workflows/%d/' % pk_workflow)
        force_authenticate(request, user=self.user)
        response = workflow_detail(request, pk = pk_workflow)
        self.assertIs(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Workflow.objects.filter(name='Workflow 1').count(), 0)



class ModuleTests(LoggedInTestCase):
    def setUp(self):
        super(ModuleTests, self).setUp()  # log in
        self.factory = APIRequestFactory()
        self.add_new_module('Module 1')
        self.add_new_module('Module 2')
        self.add_new_module('Module 3')

    def add_new_module(self, name):
        module = Module(name=name, id_name=name+'_internal', dispatch=name+'_dispatch')
        module.save()

    def test_module_list_get(self):
        request = self.factory.get('/api/modules/')
        force_authenticate(request, user=User.objects.first())
        response = module_list(request)
        self.assertIs(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]['name'], 'Module 1')
        self.assertEqual(response.data[1]['name'], 'Module 2')
        self.assertEqual(response.data[2]['name'], 'Module 3')


