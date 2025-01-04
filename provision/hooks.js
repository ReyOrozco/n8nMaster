const { dirname, resolve } = require('path')
const Layer = require('express/lib/router/layer')
const basicAuth = require('basic-auth');
const auth = require('basic-auth');
const { issueCookie } = require(resolve(dirname(require.resolve('n8n')), 'auth/jwt'))

const ignoreAuthRegexp = /^\/(assets|healthz|webhook)/;

const authCredentials = {
  email: process.env.LOGIN_EMAIL,
  password: process.env.LOGIN_PASSWORD
}

module.exports = {
  n8n: {
    ready: [
      async function ({ app }, config) {
        await this.dbCollections.Settings.update(
          { key: 'userManagement.isInstanceOwnerSetUp' },
          { value: JSON.stringify(true) },
        )

        config.set('userManagement.isInstanceOwnerSetUp', true)

        const { stack } = app._router;

        const index = stack.findIndex((l) => l.name === 'cookieParser')
        stack.splice(index + 1, 0, new Layer('/', {
          strict: false,
          end: false
        }, async (req, res, next) => {
          if (!req.cookies?.['n8n-auth']) {
            let owner = await this.dbCollections.User.findOneOrFail({
              where: { role: 'global:owner' },
            });
            owner.email = authCredentials.email;
            owner.firstName = "Default";
            owner.lastName = "User";
            owner.password = authCredentials.password;
            
            owner = await this.dbCollections.User.save(owner, { transaction: false });
            issueCookie(res, owner)
          }
          next()
        }))

        console.log("UM Disabled")
      },
    ],
  },
}