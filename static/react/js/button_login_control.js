var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

function UserGreeting(props) {
  return React.createElement(
    'h1',
    null,
    '\u0421 \u0432\u043E\u0437\u0432\u0440\u0430\u0449\u0435\u043D\u0438\u0435\u043C!'
  );
}

function GuestGreeting(props) {
  return React.createElement(
    'h1',
    null,
    '\u0412\u043E\u0439\u0434\u0438\u0442\u0435, \u043F\u043E\u0436\u0430\u043B\u0443\u0439\u0441\u0442\u0430.'
  );
}

function Greeting(props) {
  var isLoggedIn = props.isLoggedIn;
  if (isLoggedIn) {
    return React.createElement(UserGreeting, null);
  }
  return React.createElement(GuestGreeting, null);
}

function LoginButton(props) {
  return React.createElement(
    'button',
    { onClick: props.onClick },
    '\u0412\u043E\u0439\u0442\u0438'
  );
}

function LogoutButton(props) {
  return React.createElement(
    'button',
    { onClick: props.onClick },
    '\u0412\u044B\u0439\u0442\u0438'
  );
}

var LoginControl = function (_React$Component) {
  _inherits(LoginControl, _React$Component);

  function LoginControl(props) {
    _classCallCheck(this, LoginControl);

    var _this = _possibleConstructorReturn(this, (LoginControl.__proto__ || Object.getPrototypeOf(LoginControl)).call(this, props));

    _this.handleLoginClick = _this.handleLoginClick.bind(_this);
    _this.handleLogoutClick = _this.handleLogoutClick.bind(_this);
    _this.state = { isLoggedIn: false };
    return _this;
  }

  _createClass(LoginControl, [{
    key: 'handleLoginClick',
    value: function handleLoginClick() {
      this.setState({ isLoggedIn: true });
    }
  }, {
    key: 'handleLogoutClick',
    value: function handleLogoutClick() {
      this.setState({ isLoggedIn: false });
    }
  }, {
    key: 'render',
    value: function render() {
      var isLoggedIn = this.state.isLoggedIn;
      var button = void 0;
      if (isLoggedIn) {
        button = React.createElement(LogoutButton, { onClick: this.handleLogoutClick });
      } else {
        button = React.createElement(LoginButton, { onClick: this.handleLoginClick });
      }

      return React.createElement(
        'div',
        null,
        React.createElement(Greeting, { isLoggedIn: isLoggedIn }),
        button
      );
    }
  }]);

  return LoginControl;
}(React.Component);

ReactDOM.render(React.createElement(LoginControl, null), document.getElementById('button_login_control'));