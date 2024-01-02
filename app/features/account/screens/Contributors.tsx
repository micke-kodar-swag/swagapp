import React, {useEffect} from 'react';
import {
  Button,
  HStack,
  Image,
  Link,
  ScrollView,
  Text,
  VStack,
} from 'native-base';
import {useNavigation} from '@react-navigation/native';
import {NativeStackNavigationProp} from '@react-navigation/native-stack';
import {RootStackParamList} from '../../../navigation/RootStackParamList';
import {SafeAreaView, StyleSheet} from 'react-native';

const Contributor: React.FC<{
  name: string;
  githubUser: string;
  avatarUrl: string;
}> = ({name, githubUser, avatarUrl}) => (
  <HStack style={styles.contributorContainer}>
    <Image
      style={styles.contributorAvatar}
      src={avatarUrl}
      alt={`Bild på ${name}`}
    />
    <VStack style={styles.contributorTexts}>
      <Text>{name}</Text>
      <Text>
        <Link href={`https://github.com/${githubUser}`} isExternal>
          {`github.com/${githubUser}`}
        </Link>
      </Text>
    </VStack>
  </HStack>
);

const Contributors: React.FC = () => {
  const navigation =
    useNavigation<NativeStackNavigationProp<RootStackParamList>>();

  useEffect(() => {
    navigation.setOptions({
      headerLeft: () => (
        <Button
          variant="ghost"
          onPress={() => {
            navigation.pop();
          }}>
          <Text>Stäng</Text>
        </Button>
      ),
    });
  }, [navigation]);

  return (
    <SafeAreaView>
      <ScrollView contentContainerStyle={styles.scrollViewContainer}>
        <Contributor
          name="Amy Nylander"
          githubUser="Imamyable"
          avatarUrl="https://avatars.githubusercontent.com/u/37723862?v=4"
        />
        <Contributor
          name="Mikael Grön"
          githubUser="skaramicke"
          avatarUrl="https://avatars.githubusercontent.com/u/536960?v=4"
        />
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  scrollViewContainer: {
    padding: 10,
    gap: 10,
  },
  contributorContainer: {
    gap: 5,
  },
  contributorAvatar: {width: 50, height: 50},
  contributorTexts: {
    justifyContent: 'space-between',
    padding: 3,
  },
});

export default Contributors;
