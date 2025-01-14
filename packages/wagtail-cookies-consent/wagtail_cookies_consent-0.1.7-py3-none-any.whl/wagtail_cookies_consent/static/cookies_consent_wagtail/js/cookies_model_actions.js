const builder = new RequestOptionsBuilder()
  let csrf_token = document.getElementById('csrf_token').value

  cookie_consent_value = document.getElementById('cookie_consent').value
  cookie_banner = document.querySelector('.cookie-banner')
  cookies_checkboxes = document.querySelectorAll('.cookie-customize-model-checkbox')
  /*
   this button use when the user 
   selected which file cookies he want to accept
  */
  confirm_choices = document.getElementById('confirm_choices')
  /*
  this button use when the user  want just to accept all cookies after he pushed the customize setting cookies button
  */
  accept_all_cookies = document.getElementById('accept_all_cookies')
  if (cookie_consent_value != '/' && cookie_consent_value!=''  ) {
    cookie_banner.classList.add('hidden')
  }
  cookie_consent__accept = document.querySelector(".accept").addEventListener('click', accept.bind(this, 'allow'))
  /*
  this button use when the user  want just to accept all cookies after he pushed the customize setting cookies button
  */
  accept_all_cookies.addEventListener('click', accept.bind(this, 'allow'))
  cookie_consent__deny = document.querySelector(".necessary").addEventListener('click', accept.bind(this, 'deny'))
  confirm_choices.addEventListener('click', async (e) => {
    accepted = Array.from(cookies_checkboxes).map((curr) => {
      if (curr.checked) {
        return curr.name
      }
    })
    const res = await fetch('/accept_cookies/', builder.create_options('POST', {
      "X-CSRFToken": csrf_token
    }, {
      'request': 'customize',
      'accepted': accepted
    }))
  })

  async function accept(request) {
    try {
      const res = await fetch('/accept_cookies/', builder.create_options('POST', {
        "X-CSRFToken": csrf_token
      }, {
        "request": request
      }))

      cookie_banner.classList.add('hidden')

    } catch (e) {
    }
  }