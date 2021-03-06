import React from 'react'
import PropTypes from 'prop-types'
import UncontrolledDropdown from 'reactstrap/lib/UncontrolledDropdown'
import DropdownToggle from 'reactstrap/lib/DropdownToggle'
import DropdownMenu from 'reactstrap/lib/DropdownMenu'
import DropdownItem from 'reactstrap/lib/DropdownItem'
import { connect } from 'react-redux'
import { createSelector } from 'reselect'
import { addModuleAction } from '../workflow-reducer'

const numberFormat = new Intl.NumberFormat()

class Action extends React.PureComponent {
  static propTypes = {
    id: PropTypes.number.isRequired,
    title: PropTypes.string.isRequired,
    onClick: PropTypes.func.isRequired, // onClick(id) => undefined
  }

  onClick = () => {
    this.props.onClick(this.props.id)
  }

  render () {
    return (
      <DropdownItem onClick={this.onClick}>
        {this.props.title}
      </DropdownItem>
    )
  }
}

export class SelectedRowsActions extends React.PureComponent {
  static propTypes = {
    selectedRowIndexes: PropTypes.arrayOf(PropTypes.number.isRequired).isRequired,
    wfModuleId: PropTypes.number, // or null/undefined if none selected
    rowActionModules: PropTypes.arrayOf(PropTypes.shape({
      id: PropTypes.number.isRequired,
      title: PropTypes.string.isRequired
    }).isRequired).isRequired,
    onClickRowsAction: PropTypes.func.isRequired, // func(wfModuleId, moduleId, rowString) => undefined
  }

  get rowString () {
    const indexes = this.props.selectedRowIndexes
    const maxIndex = indexes.reduce((s, i) => Math.max(s, i))

    // Create `bools`, array of booleans, starts empty
    // Think of this like a bitmap
    const bools = []
    for (let i = 0; i <= maxIndex; i++) {
      bools[i] = false
    }

    // Fill in the selected indexes
    for (const selectedIndex of indexes) {
      bools[selectedIndex] = true
    }

    // Fill `parts`, an Array of [start,end] (inclusive) pairs
    const parts = []
    let curStart = null
    for (let i = 0; i <= maxIndex; i++) {
      const bool = bools[i]
      if (curStart === null && bool) {
        curStart = i
      } else if (curStart !== null && !bool) {
        parts.push([ curStart, i - 1])
        curStart = null
      }
    }
    if (curStart !== null) {
      parts.push([ curStart, maxIndex ])
    }

    const partStrings = parts.map(([ start, end ]) => {
      if (start === end) {
        return String(start + 1)
      } else {
        return `${start + 1}-${end + 1}`
      }
    })

    return partStrings.join(', ')
  }

  onClickAction = (idName) => {
    const { wfModuleId } = this.props

    this.props.onClickRowsAction(wfModuleId, idName, this.rowString)
  }

  render () {
    const { selectedRowIndexes, wfModuleId, rowActionModules } = this.props

    if (!wfModuleId || selectedRowIndexes.length === 0) return null

    const actions = rowActionModules.map(({ id, title }) => (
      <Action key={id} id={id} title={title} onClick={this.onClickAction} />
    ))

    return (
      <UncontrolledDropdown>
        <DropdownToggle title='menu' className="table-action">
          {numberFormat.format(selectedRowIndexes.length)} rows selected
        </DropdownToggle>
        <DropdownMenu right>
          {actions}
        </DropdownMenu>
      </UncontrolledDropdown>
    )
  }
}

const getModules = ({ modules }) => modules
const getRowActionModules = createSelector([ getModules ], (modules) => {
  const rowActionModules = []
  for (const key in modules) {
    const module = modules[key]
    if (module.row_action_menu_entry_title) {
      rowActionModules.push({
        id: Number(key),
        title: module.row_action_menu_entry_title
      })
    }
  }
  rowActionModules.sort((a, b) => a.title.localeCompare(b.title))

  return rowActionModules
})

function mapStateToProps (state) {
  const rowActionModules = getRowActionModules(state)

  return { rowActionModules }
}

function addWfModuleForRowsAction(currentWfModuleId, moduleId, rowsString) {
  return addModuleAction(
    moduleId,
    { afterWfModuleId: currentWfModuleId },
    { rows: rowsString }
  )
}

const mapDispatchToProps = (dispatch) => {
  return {
    onClickRowsAction: (...args) => dispatch(addWfModuleForRowsAction(...args))
  }
}

export default connect(mapStateToProps, mapDispatchToProps)(SelectedRowsActions)
