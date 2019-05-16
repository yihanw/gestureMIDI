import React, { Component } from "react";
import { ScrollView, Alert, View, Button, StyleSheet } from "react-native";
import SensorView from "./SensorView";
// import RNFetchBlob from 'react-native-fetch-blob';
import SocketIOClient from 'socket.io-client';

// //===========Code to get permission to store data in the phone. Used for data collection. Commented out for live demo======
// import {PermissionsAndroid} from 'react-native';

// async function requestStoragePermission() {
//   try {
//     const granted = await PermissionsAndroid.request(
//       PermissionsAndroid.PERMISSIONS.WRITE_EXTERNAL_STORAGE,
//       {
//         'title': 'MIDI App Download Permission',
//         'message': 'MIDI App needs access to your device storage ' +
//                    'to store data for the model.'
//       }
//     )
//     if (granted === PermissionsAndroid.RESULTS.GRANTED) {
//       console.log("You can store data")
//     } else {
//       console.log("Storage permission denied")
//     }
//   } catch (err) {
//     console.warn(err)
//   }
// }

//=====================To get sensor data=====================
const axis = ["x", "y", "z"];

export default class App extends Component {
  state = {
    accelerometer: [],
    gyroscope: [],
    record: false,
  }

  constructor(props) {
    super(props)
    this.onPressRecord = this.onPressRecord.bind(this);
    //Change this URL if the server URL changes
    this.socket = SocketIOClient('http://255bf98c.ngrok.io');
  }

  // //===========Code to store data in the phone. Used for data collection. Commented out for live demo======
  // async componentWillMount() {
  //   await requestStoragePermission()
  // }

  //function to pass to children so that they can update the current state
  handler = (sensorName, obj1) => {
    if (this.state.record){
      to_be_emitted = {
        sensorName: sensorName,
        timestamp: obj1.timestamp,
        x: obj1.x.toString().slice(0,8),
        y: obj1.y.toString().slice(0,8),
        z: obj1.z.toString().slice(0,8),
      }
      //Send the data object through websocket
      this.socket.emit('message', to_be_emitted);
    }
  }

  //Process the data from the hardware (e.g. reduce significant digit)
  processData(arr1,arr2){
    ans = []
    for (i = 0; i < Math.min(arr1.length, arr2.length); i++){
      ans.push([arr1[i], arr2[i]]);
    }
    return ans.map(
      dicts =>
      `${dicts[0].x.toString().slice(0,8)},${dicts[0].y.toString().slice(0,8)},${dicts[0].z.toString().slice(0,8)},${dicts[1].x.toString().slice(0,8)},${dicts[1].y.toString().slice(0,8)},${dicts[1].z.toString().slice(0,8)}\n`
      ).join('');
  }

  //function called when the "Collect data button" is pressed
  onPressRecord(){
    console.log("before in button", this.socket);
    console.log("after button", this.socket);
    if (this.state.record){
      //send message through web socket to stop data collection
      this.socket.emit('message', {
        sensorName: "stop"
      });
      Alert.alert('You are done sending collected data');
      this.setState({
        record: false
      })
    } else {
      Alert.alert('You are sending collected data');
      this.setState({
        record: true
      })
    }
  }

  //UI
  render() {
    return (
      <View>
        <ScrollView>
          {
            [
              SensorView ("accelerometer", ["x", "y", "z"], this.handler),
              SensorView ("gyroscope", ["x", "y", "z"], this.handler)
            ].map((Comp, index) => <Comp key={index} />)
          }
        </ScrollView>

        <Button
          onPress={this.onPressRecord}
          title="Collect Data"
        />
      </View>
    );
  }
}

//Style
const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    paddingHorizontal: 10
  },
  button: {
    alignItems: 'center',
    backgroundColor: '#DDDDDD',
    padding: 10
  }
});
