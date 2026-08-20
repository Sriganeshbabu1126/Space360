import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface AppState {
  isOnline: boolean;
}

const initialState: AppState = {
  isOnline: true, // default to true, can be updated by NetInfo later
};

const appSlice = createSlice({
  name: 'app',
  initialState,
  reducers: {
    setIsOnline: (state, action: PayloadAction<boolean>) => {
      state.isOnline = action.payload;
    },
  },
});

export const { setIsOnline } = appSlice.actions;
export default appSlice.reducer;
