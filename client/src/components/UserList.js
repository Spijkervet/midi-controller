import React from 'react';


class UserList extends React.Component {
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
    }

    createTable = () => {
      let table = []
  
      // Outer loop to create parent
      for (let i = 0; i < 3; i++) {
        let children = []
        //Inner loop to create children
        for (let j = 0; j < 5; j++) {
          children.push(<td>{`Column ${j + 1}`}</td>)
        }
        //Create the parent and add the children
        table.push(<tr>{children}</tr>)
      }
      return table
    }
  
    render() {
      return (
        <table>
          {this.createTable()}
        </table>
      );
    }
  }

  export default UserList;