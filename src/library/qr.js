import angular from 'angular';
import qr from 'qr-image';

/*
    === INSTALL ===============================================================

    requires:
        qr-image

    === CONFIG ================================================================

    import QRModule from './library/qr.js';

    add QRModule to module

    === USAGE =================================================================

    <qr-code height="200" width="200" data="mydata" error_correction="M" margin="4"></qr-code>

    https://www.npmjs.com/package/qr-image
    
*/

const ModuleName = "QR";

const QRComponent = {
    bindings: {
        data: '@',
        error_correction: '@',
        margin: '@',
        height: '@',
        width: '@',
    },
    controller: class QRCtrl {

        /* @ngInject */
        constructor($scope, $window) {
            if (DEBUG) console.log("QRCtrl: constructor", $scope.$ctrl);

            this.$scope = $scope;
            this.$window = $window;
        }

        $onInit() {
            if (DEBUG) console.log("QRCtrl: init");

            this.set_width();
            this.set_height();
            this.set_margin();
            this.set_error_correction();
            this.set_data();

            if (this.$scope.data == undefined) {
                this.$scope.event = this.$scope.$on('$locationChangeSuccess', (event) => {
                    this.image_from_url();
                });
                this.image_from_url();
                if (DEBUG) {console.log("NEW IMAGE WITH URL")}
            }
            else {
                try {
                    this.$scope.event();
                }
                catch (err) {}

                this.set_image(this.$scope.data);
                if (DEBUG) {console.log("NEW IMAGE WITH DATA")}
            }
        }

        set_width(width) {
            if (this.$scope.$ctrl.width == undefined) {
                this.$scope.width = width || 200;
            }
            else {
                this.$scope.width = this.$scope.$ctrl.width;
            }
        }

        set_height(height) {
            if (this.$scope.$ctrl.height == undefined) {
                this.$scope.height = height || 200;
            }
            else {
                this.$scope.height = this.$scope.$ctrl.height;
            }
        }

        set_margin(margin) {
            if (this.$scope.$ctrl.margin == undefined) {
                this.$scope.margin = margin || 4;
            }
            else {
                this.$scope.margin = this.$scope.$ctrl.margin;
            }
        }

        set_error_correction(ec) {
            if (this.$scope.$ctrl.error_correction == undefined) {
                this.$scope.error_correction = ec || 'M';
            }
            else {
                this.$scope.error_correction = this.$scope.$ctrl.error_correction;
            }
        }

        set_data(data) {
            this.$scope.data = this.$scope.$ctrl.data;
        }

        set_image(data) {
            this.$scope.image = qr.svgObject(
                data, {
                    type: 'svg',
                    margin: this.$scope.margin,
                    ec_level: this.$scope.error_correction,
                }
            );
        }

        image_from_url() {
            this.set_image(this.$window.location.href);
        }

    },
    template: '<svg class="qrimage" ng-attr-height="{{ height }}" ng-attr-width="{{ width }}" ng-attr-view_box="0 0 {{ image.size }} {{ image.size }}"><path ng-attr-d="{{ image.path }}"></svg>',
}

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
