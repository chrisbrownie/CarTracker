function ListBuckets() {

    iamAccessKey = document.getElementById("inputIAMAccessKey").value;
    iamSecretKey = document.getElementById("inputIAMSecretKey").value;

    AWS.config.update({
        accessKeyId: '',
        secretAccessKey: ''
    })

    AWS.config.update({
        accessKeyId: iamAccessKey,
        secretAccessKey: iamSecretKey
    });

    var s3 = new AWS.S3();

    s3.listBuckets(function (err, data) {
        if (err) {
            console.log("Error retrieving buckets:", err);
            showAlert("Error retrieving buckets: " + err);
            // TODO: Chuck something at the user to warn them 
            //       that we were unable to load buckets
        } else {
            var buckets = data.Buckets;
            // Populate the bucket list with the buckets
            var options = $("#bucket-dropdown > .dropdown-menu");
            options.html("");
            $.each(buckets, function () {
                options.append(
                    $("<a />").addClass("dropdown-item").attr("href", "#").text(this.Name).click(function () {
                        chooseBucket(this.text)
                    })
                );
            });

            $("#bucket-dropdown").show();
        }
    });
}

function chooseBucket(bucket) {

    // update the bucket variable
    bucketName = bucket;

    // update the dropdown to show the bucket name
    $("#bucketDropdownButton").html(bucketName);

    $("#listBucketObjects").show();
}

function listObjects() {

    iamAccessKey = document.getElementById("inputIAMAccessKey").value;
    iamSecretKey = document.getElementById("inputIAMSecretKey").value;

    AWS.config.update({
        accessKeyId: '',
        secretAccessKey: ''
    })

    AWS.config.update({
        accessKeyId: iamAccessKey,
        secretAccessKey: iamSecretKey
    });

    var s3 = new AWS.S3();

    var params = {
        Bucket: bucketName
    }

    s3.listObjects(params, function (err, data) {
        if (err) {
            console.log("Error retrieving bucket contents:", err);
            showAlert("Error retrieving bucket contents: " + err);
        } else {
            var objects = data.Contents;

            $("#carlog-results").html('<ul>');
            $.each(objects, function () {
                $("#carlog-results").append(
                    $("<li>").html(
                        $("<a />").text(this.Key).attr('href', '#').attr('title', this.LastModified).attr('data-key', this.Key).click({ key: this.Key }, function (event) {
                            addKmlToMap(event.data.key);
                        })
                    )
                )
            });
            $("#carlog-results").append('</ul>');
            $("#leftHandColumn").hide();
        }
    });
}

function showAlert(message) {
    $("#carlog-alert > p").html(message);
    $("#carlog-alert").show();
}

// Google Maps
function initMap() {

    var mapOptions = {
        center: new google.maps.LatLng(-37.8132, 144.963),
        zoom: 11,
        mapTypeId: google.maps.MapTypeId.HYBRID
    }

    map = new google.maps.Map(document.getElementById("carlog-map"), mapOptions);

}

function getS3KmlContents(kmlPath) {

    iamAccessKey = document.getElementById("inputIAMAccessKey").value;
    iamSecretKey = document.getElementById("inputIAMSecretKey").value;

    AWS.config.update({
        accessKeyId: '',
        secretAccessKey: ''
    })

    AWS.config.update({
        accessKeyId: iamAccessKey,
        secretAccessKey: iamSecretKey
    });

    var s3 = new AWS.S3();

    var params = {
        Bucket: bucketName,
        Key: kmlPath
    };

    s3.getObject(params, function (err, data) {
        if (err) {
            console.log("Error retrieving object:", err);
            showAlert("Error retrieving object: " + err);
        } else {
            // Put the contents of the KML into kmlContents
            resultsString = new TextDecoder("utf-8").decode(data.Body);
            return resultsString;
        }
    });
}

function addKmlToMap(kmlPath) {
    var parser, xmlDoc, kml;

    kml = getS3KmlContents(kmlPath);

    console.log("Opening map: " + kmlPath);

    console.log("kmlContents:");
    console.log(kml);
    /*
        parser = new DOMParser();
        xmlDoc = parser.parseFromString(kml, "text/xml");
    
        console.log("xmlDoc:");
        console.log(xmlDoc);
    */
}

google.maps.event.addDomListener(window, 'load', initMap);

$(document).ready(function () {

    // hide default stuff
    $("#bucket-dropdown").hide();
    $("#listBucketObjects").hide();
    //$("#carlog-map").hide();

    // click handlers
    $("#showHideLeftColumn").click(function () {
        $("#leftHandColumn").toggle(500, 'swing');
    });


    // Allow alerts to be reused
    $(".alert .close").on('click', function (e) {
        $(this).parent().hide();
    });

    // turn on all tooltips
    $('[data-toggle="tooltip"]').tooltip()

});