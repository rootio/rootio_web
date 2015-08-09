/*
 * A JQuery UI Widget to create a RRule compatible inputs for use inside a form
 * Requires: rrule.js (http://jkbr.github.io/rrule/)
 *          underscore.js
 * Author: Josh Levinger, 2013
 */

// add helpful constants to RRule
RRule.FREQUENCY_NAMES = ['year','month','week','day','hour','minute','second'];
RRule.DAYCODES = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'];
RRule.DAYNAMES = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];
RRule.MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
// note, month num for these values should be one-based, not zero-based

$.widget("rrule.recurringinput", {
  // default options
  options: {
    freq: RRule.WEEKLY,
    count: 1
  },

  _create: function() {
    //set up inputs
    // TODO: convert to underscore template
    var tmpl = "<!-- janky inline template -->";

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
    // data-freq should be lowercase value from FREQUENCY_NAMES
    
    //bymonth
    tmpl += '<div class="repeat-options controls form-inline" data-freq="monthly"><label>Only in ';
    _.each(RRule.MONTHS, function(element, index) {
      tmpl += '<label class="inline">';
      tmpl += '<input type="checkbox" name="bymonth" value="'+(index+1)+'" />';
      tmpl += element+'</label>';
    });
    tmpl += '</div>';

    //byweekday
    tmpl += '<div class="repeat-options controls form-inline" data-freq="weekly">';
    tmpl += '<label for="byweekday">On </label>';
    _.each(RRule.DAYCODES, function(element, index) {
      var d = window['RRule'][element];
      tmpl += '<label class="inline">';
      tmpl += '<input type="checkbox" name="byweekday" value="'+d.weekday+'" />';
      tmpl += RRule.DAYNAMES[index]+'</label>';
    });
    tmpl += '</div>';

    //byhour
    tmpl += '<label class="repeat-options" data-freq="hourly">Only at ';
    tmpl += '<input name="byhour" /> <span>o\'clock</span></label>';

    //byminute
    tmpl += '<label class="repeat-options" data-freq="minutely">Only at ';
    tmpl += '<input name="byminute" />  <span>minutes<span></label>';

    //bysecond
    tmpl += '<label class="repeat-options" data-freq="secondly">Only at ';
    tmpl += '<input name="bysecond" /> <span>seconds</span></label>';

    // end repeat options

    // starts on
    tmpl += '<label>Start ';
    
    var d = new Date();
    var curr_date = d.getDate();
    var curr_month = d.getMonth() + 1; //Months are zero based

    if (curr_date < 10) { curr_date = '0' + curr_date; }
    if (curr_month < 10) { curr_month = '0' + curr_month; }

    var curr_year = d.getFullYear();
    console.log(curr_year + "-" + curr_month + "-" + curr_date);
    
    tmpl += '<input name="dtstart" type="date" value="' + curr_year + "-" + curr_month + "-" + curr_date +'" />';
    tmpl += '</label>';


    // end on
    tmpl += '<div class="end-options controls">';
    tmpl += '<label for="end">End </label>';

    tmpl += '<label class="inline">';
    tmpl += '<input type="radio" name="end" value="0" checked="checked"/> Never</label>';
    tmpl += '<label class="inline">';
    tmpl += '<input type="radio" name="end" value="1" /> After <input type="number" value = "1" max="1000" min="1" name="count"/> occurences';
    tmpl += '</label>';
    tmpl += '<label class="inline">';
    tmpl += '<input type="radio" name="end" value="2"> On date <input type="date" name="until" value="' + curr_year + "-" + curr_month + "-" + curr_date +'"/>';
    tmpl += '</label>';

    tmpl += '</div>';

    // summary
    tmpl += '<label for="output">Summary ';
    tmpl += '<em id="text-output"></em></label>'; // human readable
    tmpl += '<br><label>RRule <code id="rrule-output"></code></label>'; // ugly rrule
    //TODO: show next few instances to help user debug

    //render template
    this.element.append(tmpl);

    //save input references to widget for later use
    this.frequency_select = this.element.find('select[name="freq"]');
    this.interval_input = this.element.find('input[name="interval"]');
    this.end_input = this.element.find('input[type="radio"][name="end"]');

    //bind event handlers
    this._on(this.element.find('select, input'), {
      'change': this._refresh
    });

    //set sensible defaults
    this.frequency_select.val(2);
    this.interval_input.val(1);

    //refresh
    this._refresh();
 },

  // called on create and when changing options
  _refresh: function() {
    //determine selected frequency
    var frequency = this.frequency_select.find("option:selected");
    // fill in frequency-name span
    this.element.find('#frequency_name').text(RRule.FREQUENCY_NAMES[frequency.val()]);
    // and pluralize
    if (this.interval_input.val() > 1) {
      this.element.find('#frequency_name').append('s');
    }

    // display appropriate repeat options
    var repeatOptions = this.element.find('.repeat-options');
    repeatOptions.hide();
    
    if (frequency !== "") {
      //show options for the selected frequency
      var selectedOptions = repeatOptions.filter('[data-freq='+frequency.text()+']');
      selectedOptions.show();
      
      //and clear descendent fields for the others
      nonSelectedOptions = repeatOptions.filter('[data-freq!='+frequency.text()+']');
      nonSelectedOptions.find('input[type=checkbox]:checked').removeAttr('checked');
      nonSelectedOptions.find('select').val('');
    }

    //reset end
    switch (this.end_input.filter(':checked').val()) {
      case "0":
        //never, clear count and until
        this.end_input.siblings('input[name=count]').val('');
        this.end_input.siblings('input[name=until]').val('');
        break;
      case "1":
        //after, clear until
        this.end_input.siblings('input[name=until]').val('');
        break;
      case "2":
        //date, clear count
        this.end_input.siblings('input[name=count]').val('');
        break;
    }

    //determine rrule
    var rrule = this._getRRule();

    $('#rrule-output').text(rrule.toString());
    $('#text-output').text(rrule.toText());
    this.element.trigger('rrule-update');
  },

  _getFormValues: function($form) {
    //modified from rrule/tests/demo/demo.js
    var paramObj;
    paramObj = {};

    $.each($form.serializeArray(), function(_, kv) {
      if (paramObj.hasOwnProperty(kv.name)) {
        paramObj[kv.name] = $.makeArray(paramObj[kv.name]);
        return paramObj[kv.name].push(kv.value);
      } else {
        return paramObj[kv.name] = kv.value;
      }
    });
    return paramObj;
  },
  _getRRule: function() {
    //modified from rrule/tests/demo/demo.js
    //ignore 'end', because it's part of the ui but not the spec
    values = this._getFormValues($(this.element).find('select, input[name!=end]'));

    options = {};
    getDay = function(i) {
      return [RRule.MO, RRule.TU, RRule.WE, RRule.TH, RRule.FR, RRule.SA, RRule.SU][i];
    };
    for (k in values) {
      v = values[k];
      if (!v) {
        continue;
      }
      if (_.contains(["dtstart", "until"], k)) {
        d = new Date(Date.parse(v));
        v = new Date(d.getTime() + (d.getTimezoneOffset() * 60 * 1000));
      } else if (k === 'byweekday') {
        if (v instanceof Array) {
          v = _.map(v, getDay);
        } else {
          v = getDay(v);
        }
      } else if (/^by/.test(k)) {
        if (!(v instanceof Array)) {
          v = _.compact(v.split(/[,\s]+/));
        }
        v = _.map(v, function(n) {
          return parseInt(n, 10);
        });
      } else {
        v = parseInt(v, 10);
      }
      if (k === 'wkst') {
        v = getDay(v);
      }
      if (k === 'interval' && v === 1) {
        continue;
      }
      options[k] = v;

    }
    try {
 	console.log("Try new RRule ");  
        rule = new RRule(options);
        console.log(options);
      } catch (_error) {
        e = _error;
        $("#text-output").append($('<pre class="error"/>').text('=> ' + String(e || null)));
        return;
      }
    return rule;
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
