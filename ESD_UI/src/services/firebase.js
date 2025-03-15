import firebase from 'firebase/app';
import 'firebase/auth';

// Your web app's Firebase configuration
const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "YOUR_AUTH_DOMAIN",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_STORAGE_BUCKET",
    messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
    appId: "YOUR_APP_ID"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);

// Authentication functions
export const registerUser = (email, password) => {
    return firebase.auth().createUserWithEmailAndPassword(email, password);
};

export const loginUser = (email, password) => {
    return firebase.auth().signInWithEmailAndPassword(email, password);
};

export const logoutUser = () => {
    return firebase.auth().signOut();
};

export const onAuthStateChanged = (callback) => {
    return firebase.auth().onAuthStateChanged(callback);
};

export const getCurrentUser = () => {
    return firebase.auth().currentUser;
};