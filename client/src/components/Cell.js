import React, { Component } from 'react'

class Cell extends Component {
  render() {
    return (
      <>
        <td
          className={
            this.props.valueCell === ' ' || this.props.valueCell === 'F'
              ? 'button-new-game'
              : this.props.valueCell === 'B'
              ? 'button-bomb-reveled'
              : 'button-reveled'
          }
          onClick={() =>
            this.props.checkCell(this.props.indexRow, this.props.indexCell)
          }
          onContextMenu={event =>
            this.props.flagCell(
              event,
              this.props.indexRow,
              this.props.indexCell
            )
          }
        >
        {console.log(this.props.valueCell)}
          {this.props.valueCell === 'B'
            ? '💣'
            : this.props.valueCell === 'F' || this.props.valueCell === '@'
            ? '🚩'
            : this.props.valueCell === 'E'
            ? ''
            : this.props.valueCell}
        </td>
      </>
    )
  }
}

export default Cell
