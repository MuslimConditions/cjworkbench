/**
 * Testing Stories:
 * -Renders a search bar
 * -Search bar will render suggestions of modules matching input
 * 
 */
jest.mock('./lessons/lessonSelector', () => jest.fn()) // same mock in every test :( ... we'll live

import React from 'react'
import ConnectedModuleSearch, { ModuleSearch } from './ModuleSearch'
import { mount, shallow } from 'enzyme'
import { createStore } from 'redux'
import { Provider } from 'react-redux'
import lessonSelector from './lessons/lessonSelector'

describe('ModuleSearch', () => {
  const modules = {
    4: {
      id: 4,
      name: "Load from Enigma",
      category: "Add data",
      icon: "url",
      isLessonHighlight: true,
    },
    10: {
      id: 10,
      name: "Filter by Text",
      category: "Filter",
      icon: "filter",
      isLessonHighlight: false,
    }
  }
  const modulesArray = Object.keys(modules).map(id => modules[id])

  let defaultProps
  beforeEach(() => defaultProps = {
    onClickModuleId: jest.fn(),
    onCancel: jest.fn(),
    index: 2,
    modules: modulesArray,
    isLessonHighlight: false,
  })

  describe('most tests', () => {
    let wrapper
    beforeEach(() => wrapper = mount(<ModuleSearch {...defaultProps}/>))
    afterEach(() => wrapper.unmount())

    let searchField
    beforeEach(() => searchField = wrapper.find('input[name="moduleQ"]'))

    it('matches snapshot', () => { 
      expect(wrapper).toMatchSnapshot()
    })

    it('finds all suggestions by default', () => {
      expect(wrapper.text()).toMatch(/Load from Enigma/)
      expect(wrapper.text()).toMatch(/Filter by Text/)
    })

    it('finds a suggestion matching search input', () => { 
      searchField.simulate('change', {target: {value: 'a'}})
      wrapper.update()
      expect(wrapper.text()).toMatch(/Load from Enigma/)
      expect(wrapper.text()).not.toMatch(/Filter by Text/)
    })

    it('calls onCancel on form reset (e.g., clicking button.close)', () => { 
      // search field should be empty at start
      wrapper.find('form').simulate('reset')
      expect(wrapper.prop('onCancel')).toHaveBeenCalled()
    });

    it('calls onCancel on pressing Escape', () => {
      searchField.simulate('keyDown', { keyCode: 27 })
      expect(wrapper.prop('onCancel')).toHaveBeenCalled()
    })

    it('calls onClickModuleId on click', () => {
      wrapper.find('li[data-module-name="Load from Enigma"]').simulate('click')
      expect(wrapper.prop('onClickModuleId')).toHaveBeenCalledWith(4)
    })

    it('should lesson-highlight module', () => {
      expect(wrapper.find('li[data-module-name="Load from Enigma"]').hasClass('lesson-highlight')).toBe(true)
      expect(wrapper.find('li[data-module-name="Filter by Text"]').hasClass('lesson-highlight')).toBe(false)
    })

    it('should sort modules in alphabetical order', () => {
      wrapper.unmount()
      const modules = {
        4: {
          id: 4,
          name: "Z",
          category: "Add data",
          icon: "url",
          isLessonHighlight: true,
        },
        1: {
          id: 1,
          name: "Y",
          category: "Filter",
          icon: "filter",
          isLessonHighlight: false,
        },
        6: {
          id: 6,
          name: "H",
          category: "Filter",
          icon: "filter",
          isLessonHighlight: false,
        },
        7: {
          id: 7,
          name: "A",
          category: "Add data",
          icon: "filter",
          isLessonHighlight: false,
        },
        5: {
          id: 5,
          name: "A",
          category: "Filter",
          icon: "filter",
          isLessonHighlight: false,
        }
      }
      const modulesArray = Object.keys(modules).map(id => modules[id])

      let defaultProps = {
        onClickModuleId: jest.fn(),
        onCancel: jest.fn(),
        index: 2,
        modules: modulesArray,
        isLessonHighlight: false
      }

      wrapper = mount(<ModuleSearch {...defaultProps}/>)

      let resultList = wrapper.prop('modules').map(x => x.name)
      let expectedResult = ['A', 'A', 'H', 'Y', 'Z']
      expect(resultList).toEqual(expectedResult)
    })
  })
    
  it('should highlight search box based on isLessonHighlight', () => {
    const noHighlight = shallow(<ModuleSearch {...defaultProps} isLessonHighlight={false} />)
    expect(noHighlight.hasClass('lesson-highlight')).toBe(false)

    const yesHighlight = shallow(<ModuleSearch {...defaultProps} isLessonHighlight={true} />)
    expect(yesHighlight.hasClass('lesson-highlight')).toBe(true)
  })

  describe('with store', () => {
    let store
    let wrapper
    let nonce = 0

    function highlight(index, moduleName) {
      lessonSelector.mockReturnValue({
        testHighlight: test => {
          if (index === null) return false
          return test.type === 'Module' && (test.name ? (test.name === moduleName) : true) && test.index === index
        }
      })

      // trigger a change
      store.dispatch({ type: 'whatever', payload: ++nonce })
    }

    beforeEach(() => {
      lessonSelector.mockReset()

      // Store just needs to change, to trigger mapStateToProps. We don't care
      // about its value
      store = createStore((_, action) => ({ modules, ...action.payload }), { modules })

      highlight(null)

      wrapper = mount(
        <Provider store={store}>
          <ConnectedModuleSearch {...defaultProps} alwaysRenderSuggestions={true} />
        </Provider>
      )
    })
    afterEach(() => {
      wrapper.unmount()
    })

    it('loads modules', () => {
      expect(wrapper.text()).toMatch(/Load from Enigma/)
    })

    it('highlights the search box', () => {
      highlight(2, null)
      wrapper.update()
      expect(wrapper.find('.module-search').prop('className')).toMatch(/\blesson-highlight\b/)

      highlight(1, null)
      wrapper.update()
      expect(wrapper.find('.module-search').prop('className')).not.toMatch(/\blesson-highlight\b/)
    })
  })
});

