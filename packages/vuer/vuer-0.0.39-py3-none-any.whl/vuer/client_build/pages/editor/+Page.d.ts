import { default as React } from 'react';
import { default as ReactDOM } from 'react-dom';
import * as VUER from '@vuer-ai/vuer';
import * as FIBER from '@react-three/fiber';
import * as THREE from 'three';
import * as JSX from 'react/jsx-runtime';
import * as Drei from '@react-three/drei';
import * as XR from '@react-three/xr';
import * as LEVA from 'leva';
import * as ZUSTAND from 'zustand';
declare global {
    interface Window {
        React: typeof React;
        ReactDOM: typeof ReactDOM;
        VUER: typeof VUER;
        THREE: typeof THREE;
        JSX: typeof JSX;
        FIBER: typeof FIBER;
        XR: typeof XR;
        Drei: typeof Drei;
        LEVA: typeof LEVA;
        ZUSTAND: typeof ZUSTAND;
    }
}
export default function Page(): JSX.JSX.Element | null;
