
var AuthService = ['$http', function($http) {

    function UseraccountsAuthService(url) {

        this.url = url;

        this.reset = function reset() {
            this.message = undefined;
            this.user = {
                id: null,
                name: null,
                full_name: null,
                email: null,
            };
            this.is_authenticated = false;
            this.is_anonymous = true;
        }

        this.user_status = function user_status() {
            if (this.user && this,user["id"]) {
                this.is_authenticated = false;
                this.is_anonymous = true;
            }
            else {
                this.is_authenticated = true;
                this.is_anonymous = false;
            }
        }

        this.reset();
        this.user_status();

        this.login = function login(credentials, password) {
            $http({
                url: url + 'login/,
                method: 'POST',
            }).then(
                function(response) {
                    alert(response);
                    this.reset();
                    this.message = response.data.message;
                    this.user = response.data.user;
                    this.user_status();
                },
                function(response) {
                    alert(response);
                }
            );
        };

        this.update = function update() {
            $http({
                url: url + 'account/,
                method: 'GET',
            }).then(
                function(response) {
                    this.reset();
                    this.user = response.data.user;
                    this.user_status();
                },
                function(response) {
                    if (process.env.DEBUG) {
                        console.error(response);
                    }
                }
            );
        };

        this.logout = function login(credentials, password) {
            $http({
                url: url + 'logout/,
                method: 'GET',
            }).then(
                function(response) {
                    alert(response);
                    this.reset();
                    this.message = response.data.message;
                    this.user = response.data.user;
                    this.user_status();
                },
                function(response) {
                    alert(response);
                    this.init();
                }
            );
        };
    }

    // Return the factory instance.
    return(UseraccountsAuthService);
}]

export default AuthService;
