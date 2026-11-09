import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from website.models import MenuPost, RestaurantInfo, WebsiteImage


@pytest.fixture
def website_image(db):
    return WebsiteImage.objects.create(
        name='Menu Image',
        category='menu',
        image_url='https://example.com/menu.jpg',
    )


def test_restaurant_info_string_returns_name(db):
    restaurant = RestaurantInfo.objects.create(
        name='The Great Restaurant',
        address='123 Food Street',
        contact_details='Phone: 123-456-7890',
        opening_hours='Mon-Fri: 9am - 9pm',
    )

    assert str(restaurant) == 'The Great Restaurant'


def test_website_image_string_returns_name(website_image):
    assert str(website_image) == 'Menu Image'


def test_website_image_rejects_unknown_category():
    image = WebsiteImage(
        name='Invalid Image',
        category='invalid_category',
        image_url='https://example.com/invalid.jpg',
    )

    with pytest.raises(ValidationError) as exc_info:
        image.full_clean()

    assert 'category' in exc_info.value.message_dict


def test_menu_post_string_returns_title(db, website_image):
    post = MenuPost.objects.create(
        title='Delicious Pasta',
        blurb='A new pasta dish',
        content='<p>Fresh pasta.</p>',
        image=website_image,
    )

    assert str(post) == 'Delicious Pasta'


def test_menu_post_can_be_created_without_an_image(db):
    post = MenuPost.objects.create(
        title='Image-free special',
        content='<p>Available today.</p>',
        image=None,
    )

    assert post.image is None
    assert post.created_at <= timezone.now()
