import React, { Component } from 'react'
import { Route } from 'react-router-dom'
class Options extends Component {
  constructor(props) {
    super(props)
    this.state = {
      optionGame: [[0, 'Easy'], [1, 'Intermediate'], [2, 'Expert']]
    }
  }

  render() {
    return (
      <>
        <div className="option-section">
        <h2>Start Game!</h2>
          {
            localStorage.getItem('id-game')?(
              <div>
              <Route render={({ history}) => (
                <button
                  className="button-continue-game"
                  type='button'
                  onClick={() => { history.push('/Game/0') }}
                >
                  Continue Last Game
                </button>
              )} />
              </div>
            ):""
          }
          <div>
            {this.state.optionGame.map(([value, text], i) => (
              <Route key={i} render={({ history}) => (
                <button
                  type='button'
                  className="button-new-game"
                  onClick={() => { 
                    localStorage.removeItem('id-game');
                    history.push(`/Game/${value}`) 
                  }}
                >
                  {text}
                </button>
              )} />
            ))}
          </div>
        </div>
      </>
    )
  }
}

export default Options
