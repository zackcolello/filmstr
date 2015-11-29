$(document).ready(function(){

      var options = { videoId: 'RQWSh7Db-_E', start: 105};
    //9d8wWcJLnFI
    //SwoJ-fpOnRU
    //ZwzY1o_hB5Y
    //Zz1HPLtecOg
    //RQWSh7Db-_E  : Oz
	$('#wrapper').tubular(options);

	//typeahead for search bar - TEMPORARY, will use movie DB for this later

		$('input.searchBar').typeahead({
			name: 'countries',
			local: ["Unites States", "Mexico", "Canada", "Cuba", "Guatemala"]
		});



});
