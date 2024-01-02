import {
  createNativeStackNavigator,
  NativeStackNavigationOptions,
} from '@react-navigation/native-stack';
import Profile from '../features/account/screens/Profile';
import Contributors from '../features/account/screens/Contributors';

const ProfileStack = createNativeStackNavigator();
export const ProfileStackNavigator: React.FC<{
  screenOptions: NativeStackNavigationOptions;
}> = ({screenOptions}) => {
  return (
    <ProfileStack.Navigator screenOptions={screenOptions}>
      <ProfileStack.Screen
        name="Profile"
        component={Profile}
        options={{
          title: 'Profil',
        }}
      />
      <ProfileStack.Screen
        name="Contributors"
        component={Contributors}
        options={{
          title: 'Folk som bidragit',
          presentation: 'modal',
        }}
      />
    </ProfileStack.Navigator>
  );
};
