import React, { Component } from "react";
import { StyleSheet, Text, View } from "react-native";
import * as Sensors from "react-native-sensors";

//Collect hardware data every 10 ms. (100hz)
Sensors["setUpdateIntervalForType"](Sensors["SensorTypes"].accelerometer, 10);
Sensors["setUpdateIntervalForType"](Sensors["SensorTypes"].gyroscope, 10);

//App display the x y z value of the hardware data
const Value = ({ name, value }) => (
  <View style={styles.valueContainer}>
    <Text style={styles.valueName}>{name}:</Text>
    <Text style={styles.valueValue}>{new String(value).substr(0, 8)}</Text>
  </View>
);

export default function(sensorName, values, handler) {
  const sensor$ = Sensors[sensorName];

  return class SensorView extends Component {
    constructor(props) {
      super(props);

      const initialValue = values.reduce(
        (carry, val) => ({ ...carry, [val]: 0 }),
        {}
      );
      this.state = initialValue;
    }

    componentWillMount() {
      const subscription = sensor$.subscribe(values => {
        this.setState({ ...values });
        //everytime sensor changes, it will call the handler (It's a subscription). The handler function is defined in app.js
        handler(sensorName, values);
      });
      this.setState({ subscription });
    }

    componentWillUnmount() {
      this.state.subscription.unsubscribe();
      this.setState({ subscription: null });
    }

    //UI
    render() {
      return (
        <View style={styles.container}>
          <Text style={styles.headline}>{sensorName} values</Text>
          {values.map(valueName => (
            <Value
              key={sensorName + valueName}
              name={valueName}
              value={this.state[valueName]}
            />
          ))}
        </View>
      );
    }
  };
}

//Style
const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#F5FCFF",
    marginTop: 50
  },
  headline: {
    fontSize: 30,
    textAlign: "left",
    margin: 10
  },
  valueContainer: {
    flexDirection: "row",
    flexWrap: "wrap"
  },
  valueValue: {
    width: 200,
    fontSize: 20
  },
  valueName: {
    width: 50,
    fontSize: 20,
    fontWeight: "bold"
  },
  instructions: {
    textAlign: "center",
    color: "#333333",
    marginBottom: 5
  }
});
