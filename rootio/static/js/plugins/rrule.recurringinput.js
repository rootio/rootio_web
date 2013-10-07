/*
 * A JQuery UI Widget to create a RRule compatible inputs for use inside a form
 * Requires: rrule.js (http://jkbr.github.io/rrule/)
 *          underscore.js
 * Author: Josh Levinger, 2013
 */

// add helpful constants to RRule
RRule.FREQUENCY_NAMES = ['year','month','week','day','hour','minute','second'];
RRule.DAYCODES = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'];
RRule.DAYNAMES = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

$.widget("rrule.recurringinput", {
  // default options
  options: {
    freq: RRule.WEEKLY,
    count: 1
  },

  _create: function() {
    console.log('_create');
    //set up inputs
    // TODO: convert to underscore template
    var tmpl = "";

    //frequency
    tmpl += '<label class="controls">Repeat ';
    tmpl += '<select name="freq">';
    _.each(RRule.FREQUENCIES, function(element, index) {
      var f = window['RRule'][element]; //use window[] syntax to get object from string
      tmpl += '<option value='+f+'>'+element.toLowerCase()+'</option>';
    });
    tmpl += '</select>';
    tmpl += '</label>';


    tmpl += '<label class="controls">Every ';
    tmpl += '<input type="number" value="1" min="1" max="100" name="interval"/>';
    tmpl += '&nbsp;<span id="frequency_name"></span>';
    tmpl += '</label>';

    

    // repeat options, frequency specific
    tmpl += '<div class="repeat-options controls form-inline" data-freq="weekly"><label>On ';
    _.each(RRule.DAYCODES, function(element, index) {
      var d = window['RRule'][element];
      tmpl += '<label class="inline">';
      tmpl += '<input type="checkbox" name="byweekday" value="'+d.weekday+'">'+RRule.DAYNAMES[index]+'</input>';
      tmpl += '</label>';
    });
    tmpl += '</div>';
    
    //other repeat options?

    // starts on
    //TODO

    // end on
    //TODO

    // count
    //TODO

    // summary
    // human readable rule

    // ugly rrule

    //render template
    this.element.append(tmpl);

    //save input references to widget for later use
    this.frequency_select = this.element.find('select[name="freq"]');
    this.interval_input = this.element.find('input[name="interval"]');

    //bind event handlers
    this._on(this.frequency_select, {
        'change': this._refresh
    });
    this._on(this.interval_input, {
        'change': this._refresh
    });
    
    //refresh
    this._refresh();
 },

  // called on create and when changing options
  _refresh: function() {
    console.log('_refresh');
    
    var frequency = this.frequency_select.find("option:selected");

    // fill in frequency-name span
    this.element.find('#frequency_name').text(RRule.FREQUENCY_NAMES[frequency.val()]);
    // and pluralize
    if (this.interval_input.val() > 1) {
      this.element.find('#frequency_name').append('s');
    }

    // display appropriate repeat options
    this.element.find('.repeat-options').hide();
    if (frequency !== "") {
      this.element.find('.repeat-options').filter('[data-freq='+frequency.text()+']').show();
    }


  },

  // _setOptions is called with a hash of all options that are changing
  // always refresh when changing options
  _setOptions: function() {
    this._superApply( arguments );
    this._refresh();
  },

  destroy: function() {
    // remove references
    this.frequency_select.remove();
    this.interval_input.remove();
    
    // unbind events

    // clear templated html
    this.element.html("");

    $.Widget.prototype.destroy.apply(this);
 }
});