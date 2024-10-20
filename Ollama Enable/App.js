import React, { useState, useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';

import HomeScreen from './screens/HomeScreen';
import ProfileScreen from './screens/ProfileScreen';
import SettingsScreen from './screens/SettingsScreen';
import OfflineScreen from './screens/OfflineScreen';

import * as NetInfo from '@react-native-community/netinfo';

const Stack = createStackNavigator();

export default function App() {
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    const unsubscribe = NetInfo.addEventListener((state) => {
      console.log(state);
      setIsOnline(state.isConnected);

      if (!state.isConnected) {
        // Navigate to OfflineScreen when offline
        navigationRef.current?.navigate('Offline');
      } else {
        // Navigate back to HomeScreen when back online
        navigationRef.current?.navigate('Home');
      }
    });

    return () => {
      unsubscribe();
    };
  }, []);

  const navigationRef = React.useRef(null);

  return (
    <NavigationContainer ref={navigationRef}>
      <Stack.Navigator initialRouteName={isOnline ? 'Home' : 'Offline'}>
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="Profile" component={ProfileScreen} />
        <Stack.Screen name="Settings" component={SettingsScreen} />
        <Stack.Screen name="Offline" component={OfflineScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
