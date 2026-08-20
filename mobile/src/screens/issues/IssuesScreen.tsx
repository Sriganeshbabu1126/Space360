import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function IssuesScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Issues (Placeholder)</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
});
