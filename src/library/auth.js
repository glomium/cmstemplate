import angular from 'angular';


/*
    === INSTALL ===============================================================

    requires:
        angular-jwt
        angular-local-storage

    === CONFIG ================================================================

    import AuthModule from './library/auth.js';

    add AuthModule to module

    === USAGE =================================================================

    Full angular app:
    <auth-component></auth-component>

    On user-change refresh HTTP:
    <auth-component auto-refresh></auth-component>
    
*/


const ModuleName = "Auth";


class AuthService {

    /* @ngInject */
    constructor($http, $rootScope, $interval, localStorageService, jwtHelper) {
        if (DEBUG) console.log("AuthService: constructor");
        this.$http = $http;
        this.$interval = $interval;
        this.$scope = $rootScope;
        this.$store = localStorageService;
        this.$jwt = jwtHelper;
        this.$path = '/api/';

        this.key = "auth-token";
        this.timer = undefined;

        // true if the token is refreshed
        this.refresh_token = false;

        this.update_user();
    }

    update_jwt($this) {
        if (DEBUG) console.log("AuthService: update_jwt");
        if (!$this) {
            $this = this;
        }

        $this.$http({
            url: $this.get_uri(),
            method: 'GET',
        }).then(
            function(response) {
                $this.$store.set($this.key, response.data);
                $this.update_user();
            },
            function(response) {
                if (DEBUG) console.error(response);
                // only exit the requests if the status code is 401
                if (response.status == 401) {
                    $this.$store.remove($this.key);
                    $this.update_user();
                }
                // retry to contact the auth server after 20 seconds
                else {
                    this.timer = this.$interval(this.update_jwt, 20000, 1, true, this);
                }
            }
        );
    }

    broadcast() {
        if (DEBUG) console.log("broadcast auth:user");
        this.done = true;
        this.$scope.$broadcast('auth:user', {
            user: this.user,
            is_authenticated: this.is_authenticated,
            is_anonymous: this.is_anonymous,
        });
    }

    update_user() {
        if (DEBUG) console.log("AuthService: update_user");

        this.is_authenticated = false;
        this.is_anonymous = true;
        this.user = {
            id: null,
            name: null,
            full_name: null,
            email: null,
        };

        var token = this.$store.get(this.key);

        // reset timer
        try {
            $this.timer();
        }
        catch(err) {}

        if (!token) {
            this.broadcast();
            return false;
        }

        try {
            var data = this.$jwt.decodeToken(token);
        }

        catch(err) {
            console.error("Could not decode jwt token");
            this.broadcast();
            return false;
        }

        if (!data || !data.user) {
            this.broadcast();
            return false;
        }

        if (this.$jwt.isTokenExpired(token)) {
            this.$store.remove(this.key);
            this.update_jwt();
            return false;
        }

        var expires = this.$jwt.getTokenExpirationDate(token);

        if (expires) {
            // refresh token 10 seconds before it expires
            var delta = expires - new Date() - 10000;
            if (delta < 0) {
                this.update_jwt()
            }
            else {
                this.timer = this.$interval(this.update_jwt, delta, 1, true, this);
            }
        }

        this.is_authenticated = true;
        this.is_anonymous = false;

        this.user = {
            id: data.user.id,
            name: data.user.name,
            full_name: data.user.full_name,
            email: data.user.email,
        };

        this.broadcast();
        return true;
    }

    get_uri(path) {
        if (!path) path = '';
        return this.$path + 'jwt/token/'
    }

    token() {
        var token = this.$store.get(this.key);

        if (!token) {
            if (DEBUG) console.log("AuthService: token -> NO TOKEN");
            return token;
        }

        if (!this.done) {
            this.update_user();
        }

        return token;
    }

    login(credentials, password, $this) {
        if (!$this) {
            $this = this;
        }

        $this.$http({
            url: $this.get_uri(),
            method: 'PUT',
            data: {
                credentials: credentials,
                password: password,
            },
        }).then(
            function(response) {
                $this.$store.set($this.key, response.data);
                $this.update_user();
            },
            function(response) {
                console.log(response);
                $this.$store.remove($this.key);
                $this.update_user();
            }
        );
    }

    logout($this) {
        if (!$this) {
            $this = this;
        }
        $this.$http({
            url: $this.get_uri(),
            method: 'DELETE',
        }).then(
            function(response) {
                $this.$store.remove($this.key);
                $this.update_user();
            },
            function(response) {
                $this.$scope.$broadcast('auth:logout', response);
                $this.timer = $this.$interval($this.logout, 10000, 1, true, $this);
            }
        );
    }
}

const AuthComponent = {
    bindings: {
        refresh1: '@?',
        autoRefresh: '@?',
    },
    controller: class AuthCtrl {

        /* @ngInject */
        constructor($scope, $window, AuthService) {
            if (DEBUG) console.log("AuthCtrl: constructor");

            var $this = this

            $this.user = AuthService.user;
            $scope.user = AuthService.user;
            $scope.is_authenticated = AuthService.is_authenticated && AuthService.done;
            $scope.is_anonymous = AuthService.is_anonymous && AuthService.done;

            $scope.logout = () => {
                AuthService.logout();
            }

            $scope.login = () => {
                var credentials = $scope.credentials;
                var password = $scope.password;
                AuthService.login(credentials, password);
            }

            $scope.$on('auth:user', function(event, data) {
                $scope.user = data.user;
                $scope.is_authenticated = data.is_authenticated;
                $scope.is_anonymous = data.is_anonymous;

                // reset form
                $scope.credentials = undefined;
                $scope.password = undefined;

                // check if user has changed
                if ($this.user && "autoRefresh" in $scope.$ctrl && $this.user.id != data.user.id) {
                    $window.location.reload();
                }

                // store current user
                $this.user = data.user;
            });
        }

        init() {
            if (DEBUG) console.log("AuthCtrl: init");
        }
    },
    transclude: true,
    template: '{{ user }}<br><input type="text" ng-model="credentials"><input type="password" ng-model="password"><button ng-click="logout()">logout</button><button ng-click="login()">login</button>',
}

let AuthModule = angular
.module(ModuleName, [require('angular-jwt'), require('angular-local-storage')])
.service("AuthService", AuthService)
.config(["$httpProvider", "jwtOptionsProvider", "localStorageServiceProvider", function ($httpProvider, jwtOptionsProvider, localStorageServiceProvider) {

    jwtOptionsProvider.config({
        authPrefix: 'JWT ',
        tokenGetter: ['AuthService', function(AuthService) { return AuthService.token() }],
    });

    // we use the default local storage, but with small expiration dates
    // thus everytime the browser is closed for a long(er) time the
    // JWT is invalid, but we make a request and let the web application handle
    // the usermanagement (via sessions). also we won't use the cookie-fallback storage
    localStorageServiceProvider.setDefaultToCookie(false);;

    $httpProvider.interceptors.push('jwtInterceptor');
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}])
.component('authComponent', AuthComponent)
;

if (DEBUG) {
    AuthModule.run(() => {
        console.log("loaded Module " + ModuleName);
    });
}

export default AuthModule.name;
