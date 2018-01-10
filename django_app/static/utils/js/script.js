/*
    Created on : 01 Jan, 2016, 5:00:04 PM
    Author     : Anshuman
*/

var app = angular.module('talks', []);

app.controller('app_ctrl', ['$scope','$http','$anchorScroll',
    function ($scope,$http,$anchorScroll) {
        // Utilities
        var my_utils = {
            get_admin_data:function(){
                $http({
                    method: 'GET',
                    url: base_url + 'admin/',
                }).then(function successCallback(response) {
                    $scope.user_data = response.data;
                    // console.log($scope.user_data);
                }, function errorCallback(response) {
                    console.log(response.data);
                });
            },
        };


        console.log('askdbasjhdbs')
    }]);
