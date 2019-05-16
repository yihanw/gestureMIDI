import React, { Component } from "react";
import { StyleSheet, Text, View } from "react-native";

export default class RandomView extends Component {
  constructor(props) {
    super(props);
    console.log("in constructor of child RANDOM");
    console.log(this);
    console.log(this.props);
    console.log(this.props.greeting);
  }

  render() {
    console.log("in children RANDOM");
    console.log(this.props);
    return (
      <View>
        <Text>values</Text>
      </View>
    );
  }
}
