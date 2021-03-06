import React from 'react'
import { mount } from 'enzyme'
import Workflows from './workflows'
const Utils = require('./utils');
import { okResponseMock, jsonResponseMock } from './test-utils'

describe('Workflow list page', () => {
  const testWorkflows = [
    {
      id: 1,
      name: "Charting",
      owner_name: 'Fred Frederson',
      public: true
    },
    {
      id: 7,
      name: "Messy data cleanup",
      owner_name: 'John Johnson',
      public: false
    },
    {
      id: 8,
      name: "Document search",
      owner_name: 'Sally Sallerson',
      public: true
    },
    {
      id: 9,
      name: "Visualization",
      owner_name: 'Mr. Manfrengenson',
      public: false
    },
  ]

  const addResponse = {
    id: 543,
    name: 'New Workflow',
    owner_name: 'Sally Sallerson',
    public: false,
  }

  const dupResponse = {
    id: 666,
    name: 'Copy of Visualization',
    owner_name: 'Paul Plagarizer',
    public: false,
  }

  var api;
  var wrapper;

  let globalGoToUrl
  beforeEach(() => {
    // mocking a global here... not really the greatest, ok for one test in this file
    globalGoToUrl = Utils.goToUrl
    Utils.goToUrl = jest.fn()
  })
  afterEach(() => {
    Utils.goToUrl = globalGoToUrl
  })

  let globalConfirm
  beforeEach(() => {
    globalConfirm = global.confirm
    global.confirm = jest.fn()
  })
  afterEach(() => {
    global.confirm = globalConfirm
  })

  // Load the component and give it a list of workflows, before each test
  beforeEach( () => {
    api = {
      listWorkflows: jsonResponseMock(testWorkflows),
      newWorkflow: jsonResponseMock(addResponse),
      duplicateWorkflow: jsonResponseMock(dupResponse),
      deleteWorkflow: okResponseMock()
    }

    wrapper = mount(<Workflows api={api}/>)
  })
  afterEach(() => wrapper.unmount())

  it('renders correctly', (done) => {

    // postpone until promise resolves and our workflows load
    setImmediate( () => {
      wrapper.update()
      expect(wrapper).toMatchSnapshot();

      expect(api.listWorkflows.mock.calls.length).toBe(1);

      // Make sure there is a context menu for each workflow
      var menus = wrapper.find('.menu-test-class');
      expect(menus).toHaveLength(4)

      // Make sure there is a metadata line for each workflow in the list
      menus = wrapper.find('.wf-meta--id');
      expect(menus).toHaveLength(4)

      done();
    })
  });

  it('delete a workflow', (done) => {
    global.confirm.mockReturnValue(true) // pretend the user clicked OK
    wrapper.instance().deleteWorkflow(9) // invoke the callback passed to child menu component

    // We've clicked delete and now we have to wait for everything to update.
    // see https://facebook.github.io/jest/docs/asynchronous.html
    setImmediate(() => {
      wrapper.update()
      expect(api.deleteWorkflow.mock.calls.length).toBe(1)
      expect(api.deleteWorkflow.mock.calls[0][0]).toBe(9)
      expect(wrapper.find('.workflow-item')).toHaveLength(3) // one fewer workflow
      done()
    })
  })


  it('new workflow button', (done) => {
    // let 4 workflows load
    setImmediate( () => {
      var newButton = wrapper.find('.new-workflow-button');
      newButton.first().simulate('click');

      setImmediate(() => {
        expect(api.newWorkflow).toHaveBeenCalled()
        expect(Utils.goToUrl).toHaveBeenCalledWith('/workflows/543')
        done()
      })
    })
  })

  it('duplicate workflow callback', (done) => {
    // let 4 workflows load
    setImmediate( () => {
      wrapper.update()
      expect(wrapper.find('.workflow-item')).toHaveLength(4)
      wrapper.instance().duplicateWorkflow(9)

      // should be a new item at the top of the list
      setImmediate(() => {
        wrapper.update()
        expect(api.duplicateWorkflow.mock.calls.length).toBe(1)
        expect(api.duplicateWorkflow.mock.calls[0][0]).toBe(9)

        expect(wrapper.find('.workflow-item')).toHaveLength(5)

        done()
      })
    })
  })
})
