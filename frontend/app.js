var myApp = angular.module("myApp", ["ngRoute", "ngResource", "myApp.services"]);

var services = angular.module("myApp.services", ["ngResource"])
services
.factory('Actor', function($resource) {
    return $resource('http://localhost:5000/api/v1/actors/:id', {id: '@id'}, {
        get: { method: 'GET' },
        delete: { method: 'DELETE' }
    });
})
.factory('Actors', function($resource) {
    return $resource('http://localhost:5000/api/v1/actors', {}, {
        query: { method: 'GET', isArray: true },
        create: { method: 'POST', }
    });
})
.factory('Title', function($resource) {
    return $resource('http://localhost:5000/api/v1/titles/:id', {id: '@id'}, {
        get: { method: 'GET' },
        delete: { method: 'DELETE' }
    });
})
.factory('Titles', function($resource) {
    return $resource('http://localhost:5000/api/v1/titles', {}, {
        query: { method: 'GET', isArray: true},
        create: { method: 'POST', }
    });
})
.factory('Search', function($resource) {
    return $resource('http://localhost:5000/api/v1/search', {q: '@q'}, {
        query: { method: 'GET', isArray: true}
    });
  })
.factory('Search2', function($resource) {
    return $resource('http://localhost:5000/api/v1/search2', {q: '@q'}, {
        query: { method: 'GET', isArray: true}
    });
});

myApp.config(function($routeProvider) {
    $routeProvider
    .when('/', {
        templateUrl: 'pages/main.html',
        controller: 'mainController'
    })
    .when('/s', {
        templateUrl: 'pages/main2.html',
        controller: 'mainController2'
    })
    .when('/newActor', {
        templateUrl: 'pages/actor_new.html',
        controller: 'newActorController'
    })
    .when('/actors', {
        templateUrl: 'pages/actors.html',
        controller: 'actorListController'
    })
    .when('/actors/:id', {
        templateUrl: 'pages/actor_details.html',
        controller: 'actorDetailsController'
    })
    .when('/newTitle', {
        templateUrl: 'pages/title_new.html',
        controller: 'newTitleController'
    })
    .when('/titles', {
        templateUrl: 'pages/titles.html',
        controller: 'titleListController'
    })
    .when('/titles/:id', {
        templateUrl: 'pages/title_details.html',
        controller: 'titleDetailsController'
    })
});

myApp.filter('filterTitles', function() {
  return function(input) {
    var output = new Array();
    for (i=0; i<input.length; i++) {
        if (input[i].checked == true) {
            output.push(input[i].name);
        }
    }
    return output;
  }
});

myApp.controller(
    'mainController',
    function ($scope, Search) {
        $scope.search = function() {
            q = $scope.searchString;
            if (q.length > 1) {
                $scope.results = Search.query({q: q});
            }
        };
    }
);

myApp.controller(
    'mainController2',
    function ($scope, Search2) {
        $scope.search2 = function() {
            q = $scope.searchString2;
            if (q.length > 1) {
                $scope.results = Search2.query({q: q});
            }
        };
    }
);

myApp.controller(
    'newActorController',
    function ($scope, Titles, Actors, $location, $timeout, $filter) {
        $scope.titles = Titles.query();
        $scope.insertActor = function () {
            $scope.actor.titles = $filter('filterTitles')($scope.titles);
            Actors.create($scope.actor);
            $timeout(function (){
                $location.path('/actors').search({'created': $scope.actor.first_name});
            }, 500);
        };
        $scope.cancel = function() {
            $location.path('/actors');
        };
    }

);
myApp.controller(
    'newTitleController',
    function ($scope,Titles,Title,$location, $timeout, $filter) {
        $scope.insertTitle = function () {
            Titles.create($scope.title);
            $timeout(function (){
                $location.path('/titles').search2({'created': $scope.title.short_title});
            }, 500);
        };
        $scope.cancel2 = function() {
            $location.path('/titles');
        };
    }

);

myApp.controller(
    'actorListController',
    function ($scope, Actors, Actor, $location, $timeout) {
        if ($location.search().hasOwnProperty('created')) {
            $scope.created = $location.search()['created'];
        }
        if ($location.search().hasOwnProperty('deleted')) {
            $scope.deleted = $location.search()['deleted'];
        }
        $scope.deleteActor = function(actor_id) {
            var deleted = Actor.delete({id: actor_id});
            $timeout(function(){
                $location.path('/actors').search({'deleted': 1})
            }, 500);
            //$scope.actors = actors.query();
        };
        $scope.actors = Actors.query();
    }
);

myApp.controller(
    'titleListController',
    function ($scope, Titles, Title, $location, $timeout) {
        if ($location.search().hasOwnProperty('created')) {
            $scope.created = $location.search2()['created'];
        }
        if ($location.search().hasOwnProperty('deleted')) {
            $scope.deleted = $location.search2()['deleted'];
        }
        $scope.deleteTitle = function(title_id) {
            var deleted = Title.delete({id: title_id});
            $timeout(function(){
                $location.path('/titles').search2({'deleted': 1})
            }, 500);
            //$scope.titles = titles.query();
        };
        $scope.titles = Titles.query();
    }
);

myApp.controller(
    'actorDetailsController', ['$scope', 'Actor', '$routeParams',
    function ($scope, Actor, $routeParams) {
        $scope.actor = Actor.get({id: $routeParams.id});
    }
]);

myApp.controller(
    'titleDetailsController', ['$scope', 'Title', '$routeParams',
    function ($scope, Title, $routeParams) {
        $scope.title = Title.get({id: $routeParams.id});
    }
]);
