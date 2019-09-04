import React from 'react';
import PropTypes from "prop-types";

import sendMidiEvent from '../App'

// AudioPad

class AudioPad extends React.Component {
    constructor(props) {
      super(props);

      const { width, height, color, margin } = this.props;

      this.state = {
        hover: false
      };

      this.audioBlock = {
        display: "inline-block",
        margin: `${margin}px`
      };

      this.defaultStyle = {
        width: `${width}px`,
        height: `${height}px`,
        backgroundColor: "#717273",
        borderRadius: "2px",
        boxShadow: "0px 0px 16px 1px rgba(0,0,0,0.75)"
      };

      this.hoverStyle = {
        width: `${width}px`,
        height: `${height}px`,
        borderRadius: "2px",
        boxShadow: `0px 0px 16px 1px ${color}`,
        backgroundColor: "#9499A2",
        transition: "0.05s"
      };
  
      this.handleEvent = this.handleEvent.bind(this);
    }
  
    componentDidMount() {
      const { keyCode, keyUp } = this.props
      console.log('pad initiated')
    }

    sendMidiEvent = (note_on, pitch, velocity, channel) => {
        this.props.midiEvent(note_on, pitch, velocity, channel);
    }
  
    handleEvent = (event) => {
      console.log(event)
      if (event.type === "touchstart") {// || event.type === "mousedown") {
        this.setState({ hover: true });
        this.sendMidiEvent(144, parseInt(this.props.keyCode), 127);
      } else {
        this.setState({ hover: false });
      }
    }
  
    render() {
      return (
        <div style={this.audioBlock} onTouchStart={ this.handleEvent } onTouchEnd={ this.handleEvent } onMouseDown={ this.handleEvent } onMouseUp={ this.handleEvent }>
          <div
            style={
              this.state.hover === true ? this.hoverStyle : this.defaultStyle
            }
          />
          <p>{this.props.children}</p>
        </div>
      );
    }
  }
  
  AudioPad.propTypes = {
      volume: PropTypes.number,
      width: PropTypes.number,
      height: PropTypes.number,
      margin: PropTypes.number,
      color: PropTypes.string,
      keyCode: PropTypes.number,
      keyUp: PropTypes.bool
  };
  AudioPad.defaultProps = {
      width: 200,
      height: 200,
      margin: 50,
      color: "#5f5f5f",
      keyUp: false
  };

  export default AudioPad;