import angular from 'angular';

/*
    === INSTALL ===============================================================

    import ResponsiveModule from './library/responsive.js';

    add ResponsiveModule to module

    === USAGE =================================================================
    
*/

const ModuleName = "Responsive";

class ResponsiveService {
    /* @ngInject */
    constructor($window, $rootScope) {
        if (DEBUG) console.log(ModuleName + "Service: constructor");

        this.$scope = $rootScope;
        this.breakpoint = undefined;

        angular.element($window).bind('resize', () => {
            this.resize($window.innerWidth);
        });

        this.resize($window.innerWidth);
    }

    resize(size) {
        // if (DEBUG) console.log(ModuleName + "Service: resize(" + size + ")");

        var breakpoint = this.breakpoint;
        var breakpoint_value = undefined;

        this.breakpoint = undefined;

        for (var key in BREAKPOINTS) {
            var value = parseInt(BREAKPOINTS[key]);

            // console.log(size, value, value <= size, breakpoint_value < value, breakpoint_value, this.breakpoint, key);
            if (!this.breakpoint || value <= size && breakpoint_value > size) {
                this.breakpoint = key;
                breakpoint_value = value;
            }
        }

        if (this.breakpoint != breakpoint) {
            if (DEBUG) console.log(ModuleName + "Service: NEW BREAKPOINT " + this.breakpoint);
            this.$scope.$broadcast('responsive:breakpoint', this.breakpoint);
        }
    }
}

class ResponsiveDirective {
    constructor() {
        if (DEBUG) console.log(ModuleName + "Directive: constructor");
        this.restrict = "A";
        this.template = '<img>';
        this.transclude = false;
        this.scope = {};
    }

    /* @ngInject */
    controller($scope, ResponsiveService) {

        $scope.breakpoint = ResponsiveService.breakpoint;

        $scope.$on('responsive:breakpoint', (event, breakpoint) => {
            $scope.breakpoint = breakpoint;
            $scope.calc_image();
        });

        $scope.calc_image = () => {
            $scope.image = '/cached/' + $scope.render + '/' + $scope.breakpoint + $scope.source;
            // update image source
            $scope.element.src = $scope.image;
        }
    }

    link(scope, element, attrs) {
        scope.render = attrs.ngResponsive;
        scope.source = attrs.source || attrs.src;
        scope.element = element[0];

        scope.calc_image();
    }
}

let Module = angular
.module(ModuleName, [])
.service("ResponsiveService", ResponsiveService)
.directive('ngResponsive', () => new ResponsiveDirective)
;

if (DEBUG) {
    Module.run(() => {
        console.log("loaded Module " + ModuleName);
    });
}

export default ModuleName;
