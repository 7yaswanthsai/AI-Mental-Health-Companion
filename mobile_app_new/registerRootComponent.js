import { AppRegistry } from 'react-native';

export function registerRootComponent(component) {
  AppRegistry.registerComponent('main', () => component);

  return component;
}
