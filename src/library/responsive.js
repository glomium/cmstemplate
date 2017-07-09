import angular from 'angular';

/*
import { EventEmitter } from '@angular/core';
import { Injectable } from '@angular/core';
// import { Optional } from '@angular/core';

import { Observable } from 'rxjs';

@Injectable()
export class ResponsiveService {

    private breakpoint: string;
    private breakpoints: { [index: string]: number; };
    private observer: any;

    public changes = new EventEmitter<string>();

    constructor() {
        // TODO: make breakpoints configurable
        this.breakpoints = {
            'xs': 0,
            'sm': 768,
            'md': 992,
            'lg': 1200,
            'xl': 1600,
        }
        this.observer = Observable.fromEvent(window, 'resize').debounceTime(100).subscribe((event) => {
            this.resize();
        });
        this.resize();
    }

    get(): string {
        return this.breakpoint;
    }

    set(breakpoint: string): void {
        this.breakpoint = breakpoint;
        this.changes.emit(breakpoint);
    }

    resize(): void {
        var breakpoint: string;
        var selected = -1;
        for (var key in this.breakpoints) {
            var value = this.breakpoints[key];
            if (value <= window.innerWidth && selected < value) {
                selected = value;
                breakpoint = key;
            }
        }
        if(breakpoint && breakpoint != this.breakpoint) {
            this.set(breakpoint);
        }
    }
}


@Injectable()
export class ResponsiveImage {

    private grid: string;

    constructor(private responsive: ResponsiveService) {
        // TODO: make service-url configureable

        this.grid = this.responsive.get();
        this.responsive.changes.subscribe((update:string) => {
            this.grid = update;
        });
    }

    img(url: string, context: string, extension: string): string {
        if (extension === undefined) {
            extension = 'jpg';
        }
        if (context === undefined) {
            return url + '__' + this.grid + '.' + extension;
        }
        else {
            return url + '__' + context + '_' + this.grid + '.' + extension;
        }
    }
}
*/

/*
    === INSTALL ===============================================================

    import ResponsiveModule from './library/responsive.js';

    add ResponsiveModule to module

    === USAGE =================================================================

    <qr-code height="200" width="200" data="mydata" error_correction="M" margin="4"></qr-code>

    https://www.npmjs.com/package/qr-image
    
*/

const ModuleName = "Responsive";

let Module = angular
.module(ModuleName, [])
.component('qrCode', QRComponent)
;

if (DEBUG) {
    Module.run(() => {
        console.log("loaded Module " + ModuleName);
    });
}

export default ModuleName;
