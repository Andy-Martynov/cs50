'use strict';

function FormattedDate(props) {
  return /*#__PURE__*/React.createElement("span", {className:"w3-text-black m-0 p-0"}, props.date.toLocaleTimeString(), ".");
}

class Clock extends React.Component {
  constructor(props) {
    super(props);
    this.state = { date: new Date() };
  }

  componentDidMount() {
    this.timerID = setInterval(
    () => this.tick(),
    1000);

  }

  componentWillUnmount() {
    clearInterval(this.timerID);
  }

  tick() {
    this.setState({
      date: new Date() });

  }

  render() {
    return /*#__PURE__*/(
      React.createElement("div", {className:"w3-button w3-red w3-round w3-round-xlarge p-1 m-0"}, /*#__PURE__*/
      React.createElement(FormattedDate, { date: this.state.date })));
  }}


function App() {
  return /*#__PURE__*/(
    React.createElement("div", null, /*#__PURE__*/
    React.createElement(Clock, null)));


}

// ReactDOM.render( /*#__PURE__*/React.createElement(App, null), document.getElementById('clocks'));

// Find all DOM containers, and render Clocks into them.
document.querySelectorAll('.clock')
  .forEach(domContainer => {
    ReactDOM.render(
      e(Clock, ),
      domContainer
    );
  });



