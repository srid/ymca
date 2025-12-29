#!/usr/bin/env python3
"""
Parses YMCA schedule HTML files and outputs structured JSON.

Usage: python parse_schedule.py schedules/2026-q1-group-swim.html > schedules/2026-q1-group-swim.json
"""

import sys
import json
import re
from html.parser import HTMLParser


class ScheduleParser(HTMLParser):
    """
    Parses YMCA schedule HTML tables into structured event data.
    
    The HTML structure has tables for each section (Group lessons - Morning, etc.)
    with 7 columns (Monday-Sunday) and multiple rows of events.
    """
    
    DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    def __init__(self):
        super().__init__()
        self.events = {day: [] for day in self.DAYS}
        self.meta = {
            "season": "",
            "start_date": "",
            "end_date": "",
            "source": "YMCA Saint-Roch (Québec)",
            "notes": ""
        }
        
        # Parsing state
        self.in_table = False
        self.in_thead = False
        self.in_tbody = False
        self.in_td = False
        self.in_tr = False
        self.in_course_title = False
        self.in_course_infos = False
        self.current_section = ""
        self.current_col = -1
        self.current_row_events = []  # Events for current row
        self.current_event = {}
        self.current_info_type = None
        self.text_buffer = ""
        self.span_depth = 0  # Track span nesting
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        classes = attrs_dict.get('class', '').split()
        
        if tag == 'table' and 'programmation-panel-course-table' in classes:
            self.in_table = True
        elif tag == 'thead':
            self.in_thead = True
        elif tag == 'tbody':
            self.in_tbody = True
        elif tag == 'tr' and self.in_tbody:
            self.in_tr = True
            self.current_col = -1
        elif tag == 'td' and self.in_tr:
            self.in_td = True
            self.current_col += 1
            self.current_event = {}
        elif tag == 'p' and 'course-title' in classes:
            self.in_course_title = True
            self.text_buffer = ""
        elif tag == 'span' and 'course-infos' in classes:
            self.in_course_infos = True
            self.text_buffer = ""
            self.span_depth = 0
            # Check for icon type in nested span
        elif tag == 'span' and self.in_course_infos:
            self.span_depth += 1
            # Detect info type from icon class
            if 'icon-clock-wrapper' in classes:
                self.current_info_type = 'time'
            elif 'icon-pin-wrapper' in classes:
                self.current_info_type = 'location'
            elif 'icon-avatar-wrapper' in classes:
                self.current_info_type = 'instructor'
            elif 'icon-flag-outline-wrapper' in classes:
                self.current_info_type = 'intensity'
            elif 'icon-infos-outline-wrapper' in classes:
                self.current_info_type = 'lanes'
        elif tag == 'th' and 'table-print-header' in classes:
            self.text_buffer = ""
                
    def handle_endtag(self, tag):
        if tag == 'table':
            self.in_table = False
        elif tag == 'thead':
            self.in_thead = False
        elif tag == 'tbody':
            self.in_tbody = False
        elif tag == 'tr' and self.in_tr:
            self.in_tr = False
        elif tag == 'td' and self.in_td:
            self.in_td = False
            # Save event if we have data
            if self.current_event and 'activity' in self.current_event:
                day = self.DAYS[self.current_col] if 0 <= self.current_col < 7 else None
                if day:
                    self.events[day].append(self.current_event)
            self.current_event = {}
        elif tag == 'p' and self.in_course_title:
            self.in_course_title = False
            activity = self.text_buffer.strip()
            if activity:
                self.current_event['activity'] = activity
        elif tag == 'span' and self.in_course_infos:
            if self.span_depth > 0:
                self.span_depth -= 1
            else:
                # End of course-infos span - process the collected text
                self.in_course_infos = False
                value = self.text_buffer.strip()
                if value and self.current_info_type:
                    self._process_info_value(value)
                self.current_info_type = None
        elif tag == 'th':
            section = self.text_buffer.strip()
            if section and ('Group lessons' in section or 'Lane swim' in section):
                self.current_section = section
                
    def _process_info_value(self, value: str):
        """Process a course info value based on the current info type."""
        if self.current_info_type == 'time':
            # Parse "HH:MM to HH:MM" into start and end
            match = re.match(r'(\d{1,2}):(\d{2})\s+to\s+(\d{1,2}):(\d{2})', value)
            if match:
                self.current_event['start'] = f"{int(match.group(1)):02d}:{match.group(2)}"
                self.current_event['end'] = f"{int(match.group(3)):02d}:{match.group(4)}"
        elif self.current_info_type == 'lanes':
            # Parse "N swimming lanes" into integer
            match = re.match(r'(\d+)\s+swimming\s+lanes?', value)
            if match:
                self.current_event['lanes'] = int(match.group(1))
        elif self.current_info_type == 'location':
            self.current_event['location'] = value
        elif self.current_info_type == 'instructor':
            self.current_event['instructor'] = value
        elif self.current_info_type == 'intensity':
            self.current_event['intensity'] = value.lower()
                
    def handle_data(self, data):
        if self.in_course_title or self.in_course_infos:
            self.text_buffer += data
        elif self.in_thead:
            self.text_buffer += data
            
    def get_result(self):
        """Return the parsed schedule as a dict."""
        # Sort each day's events by start time
        for day in self.DAYS:
            self.events[day].sort(key=lambda e: e.get('start', '99:99'))
        
        return {
            "meta": self.meta,
            "events": self.events
        }


def parse_schedule(html_path: str) -> dict:
    """Parse an HTML schedule file and return structured data."""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    parser = ScheduleParser()
    parser.feed(content)
    
    result = parser.get_result()
    
    # Try to extract meta from the HTML - look for session dates
    date_match = re.search(r'(\w+ \d+, \d{4})\s*-\s*(\w+ \d+, \d{4})', content)
    if date_match:
        from datetime import datetime
        try:
            start = datetime.strptime(date_match.group(1), '%B %d, %Y')
            end = datetime.strptime(date_match.group(2), '%B %d, %Y')
            result['meta']['start_date'] = start.strftime('%Y-%m-%d')
            result['meta']['end_date'] = end.strftime('%Y-%m-%d')
        except ValueError:
            pass
    
    # Look for season name
    season_match = re.search(r'selected="selected" value="\d+">([^<]+)</option>', content)
    if season_match:
        result['meta']['season'] = season_match.group(1).strip()
    
    # Standard notes
    result['meta']['notes'] = (
        "The YMCA reserves the right to cancel classes if there are fewer than 10 participants. "
        "The instructor may be changed without notice. "
        "Lane Swim (City) sessions have no membership requirement and may be more crowded."
    )
    
    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: parse_schedule.py <html_file>", file=sys.stderr)
        sys.exit(1)
    
    html_path = sys.argv[1]
    result = parse_schedule(html_path)
    
    # Output formatted JSON
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
