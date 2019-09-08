import React from 'react';



class UsernameForm extends React.Component {
    constructor(props) {
      super(props);
      this.state = {value: ''};
  
      this.handleChange = this.handleChange.bind(this);
      this.handleSubmit = this.handleSubmit.bind(this);
    }
  
    handleChange(event) {
      this.setState({value: event.target.value});
    }
  
    handleSubmit(event) {
      console.log('A name was submitted: ' + this.state.value);
      event.preventDefault();
      this.props.joinMidi(this.state.value)
    }
  
    render() {
      return (
        <form onSubmit={this.handleSubmit}>
          <label>
            <input className="username-field" type="text" placeholder="Username" value={this.state.value} onChange={this.handleChange} />
          </label>
        </form>
      );
    }
  }

  export default UsernameForm;