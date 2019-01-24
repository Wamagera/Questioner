""" Test for Meetups."""
import json
from .base_test import BaseTest


class TestMeetup(BaseTest):
    """Test class for meetups."""

    def test_get_meetups(self):
        """Test for getting all meetups"""
        with self.client as c:
            headers = {"Content-Type": self.mime_type}
            meetups_response = c.get('/api/v1/meetups/upcoming',
                                     headers=headers)
            response = json.loads(meetups_response.data.decode('utf-8'))

            self.assertEqual(meetups_response.status_code, 200)
            self.assertEqual(response['status'], 200)
            self.assertIn("data", response)

    def test_create_meetup(self):
        """Test for creating a new meetup"""
        with self.client as c:

            headers = {"Content-Type": self.mime_type}
            c.post('/api/v1/signup',
                   json=self.user1,
                   headers=headers)
            login = c.post('/api/v1/login',
                           json=self.login_payload,
                           headers=headers)
            login_resp = json.loads(login.data.decode('utf-8'))

            self.assertIn("token", login_resp)

            token = login_resp['token']
            header_extra = {
                "Content-type": self.mime_type,
                "X-ACCESS-TOKEN": token
                }

            post_meetup = c.post('/api/v1/meetups',
                                 json=self.meetup_payload,
                                 headers=header_extra)
            meetup_res = json.loads(post_meetup.data.decode('utf-8'))

            self.assertEqual(meetup_res['message'],
                             "Meetup created successfully!")

    def test_create_meetup_with_tags_list(self):
        """Test for creating a new meetup"""
        with self.client as c:

            headers = {"Content-Type": self.mime_type}
            self.meetup_payload2 = {
                "topic": "Bootcamp 37 retreat",
                "location": "Andela, Nairobi",
                "happeningOn": "2:00pm 6th Feb 2019",
                "tags": ["django,flask"]
                    }
            c.post('/api/v1/signup',
                   json=self.user1,
                   headers=headers)
            login = c.post('/api/v1/login',
                           json=self.login_payload,
                           headers=headers)
            login_resp = json.loads(login.data.decode('utf-8'))

            self.assertIn("token", login_resp)

            token = login_resp['token']
            header_extra = {
                "Content-type": self.mime_type,
                "X-ACCESS-TOKEN": token
                }

            post_meetup = c.post('/api/v1/meetups',
                                 json=self.meetup_payload2,
                                 headers=header_extra)
            meetup_res = json.loads(post_meetup.data.decode('utf-8'))

            self.assertEqual(meetup_res['message'],
                             "Meetup created successfully!")

    def test_create_meetup_topic_with_less_than_required_characters(self):
        """Test for creating a new meetup"""
        with self.client as c:

            headers = {"Content-Type": self.mime_type}
            c.post('/api/v1/signup',
                   json=self.user1,
                   headers=headers)
            login = c.post('/api/v1/login',
                           json=self.login_payload,
                           headers=headers)
            login_resp = json.loads(login.data.decode('utf-8'))

            self.assertIn("token", login_resp)

            token = login_resp['token']
            header_extra = {
                "Content-type": self.mime_type,
                "X-ACCESS-TOKEN": token
                }

            post_meetup = c.post('/api/v1/meetups',
                                 json=self.meetup_payload0,
                                 headers=header_extra)
            meetup_res = json.loads(post_meetup.data.decode('utf-8'))

            self.assertEqual(meetup_res['error'], "The topic field requires" \
                             " a minimum number of 10 characters")

    def test_create_meetup_location_with_less_than_required_characters(self):
        """Test for creating a new meetup"""
        with self.client as c:

            headers = {"Content-Type": self.mime_type}
            c.post('/api/v1/signup',
                   json=self.user1,
                   headers=headers)
            login = c.post('/api/v1/login',
                           json=self.login_payload,
                           headers=headers)
            login_resp = json.loads(login.data.decode('utf-8'))

            self.assertIn("token", login_resp)

            token = login_resp['token']
            header_extra = {
                "Content-type": self.mime_type,
                "X-ACCESS-TOKEN": token
                }

            post_meetup = c.post('/api/v1/meetups',
                                 json=self.meetup_payload1,
                                 headers=header_extra)
            meetup_res = json.loads(post_meetup.data.decode('utf-8'))

            self.assertEqual(meetup_res['error'], "The location field " \
                             "requires a minimum number of 10 characters")

    def test_rsvp(self):
        """Test for rsvp to a meetup"""
        with self.client as c:
            headers = {"Content-Type": self.mime_type}
            self.meetup_payload = {
                "topic": "Bootcamp 35 rovers",
                "location": "Andela, Nairobi",
                "happeningOn": "2:00pm 6th Feb 2019",
                "tags": ["django,flask"]
                    }
            c.post('/api/v1/signup',
                   json=self.user1,
                   headers=headers)

            login = c.post('/api/v1/login',
                           json=self.login_payload,
                           headers=headers)
            login_resp = json.loads(login.data.decode('utf-8'))

            self.assertIn("token", login_resp)

            token = login_resp['token']
            header_extra = {
                "Content-type": self.mime_type,
                "X-ACCESS-TOKEN": token
            }

            post_meetup = c.post('/api/v1/meetups',
                                 json=self.meetup_payload,
                                 headers=header_extra)
            meetup_res = json.loads(post_meetup.data.decode('utf-8'))

            self.assertEqual(meetup_res['message'],
                             "Meetup created successfully!")

            rsvp_payload = {"response": "maybe"}
            rsvp_meetup = c.post('/api/v1/meetups/1/rsvps',
                                 json=rsvp_payload,
                                 headers=header_extra)
            rsvp_res = json.loads(rsvp_meetup.data.decode('utf-8'))

            self.assertEqual(rsvp_res['message'], "RSVP created successfully!")
