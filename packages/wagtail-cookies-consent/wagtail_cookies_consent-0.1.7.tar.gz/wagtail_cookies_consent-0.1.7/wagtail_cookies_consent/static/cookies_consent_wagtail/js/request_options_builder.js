class RequestOptionsBuilder {
    /**
     * Creates options for HTTP requests.
     * @param {string} method - HTTP method (POST, DELETE, UPDATE, GET).
     * @param {object} headers - HTTP headers.
     * @param {object} body - Request body.
     * @returns {object} Options for the HTTP request.
     */

    create_options(method, headers, body) {
      const allowedMethod = ['POST', 'DELETE', 'UPDATE', 'GET']
      if (!allowedMethod.includes(method))
        throw new Error(`Invalid method: ${method}.  Allowed methods are: ${allowedMethod.join(',')}`)
      return {
        method: method,
        headers: headers,
        body: JSON.stringify(body)

      }
    }
  }