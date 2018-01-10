import {Component, OnInit} from '@angular/core';

// var AES = require('crypto-js/aes');
// var enc = require('crypto-js/enc');
// var lib = require('crypto-js/lib');
// var pad = require('crypto-js/pad');
// var mode = require('crypto-js/mode-cbc');
// var PBKDF2 = require('crypto-js/PKDBF2');
// var CryptoJS = require('crypto-js');
import jwtDecode from 'jwt-decode';
import {ES256} from '../../Pyth/ES256';
import {ES384} from '../../Pyth/ES384';
import {ES512} from '../../Pyth/ES512';
import {HS256} from '../../Pyth/HS256';
import {HS384} from '../../Pyth/HS384';
import {HS512} from '../../Pyth/HS512';
import {PS256} from '../../Pyth/PS256';
import {PS384} from '../../Pyth/PS384';
import {PS512} from '../../Pyth/PS512';
import {RS256} from '../../Pyth/RS256';
import {RS384} from '../../Pyth/RS384';
import {RS512} from '../../Pyth/RS512';
import {AES, enc, lib, pad, mode, PBKDF2, SHA256} from 'crypto-js';
// import {CryptoJs} from 'crypto-js';
import {origTxt} from '../../Pyth/orig-txt';
// import {encryptedText} from '../../Pyth/aes-enc';


const MyPad = {
  pad: function (data, blockSize) {
    const num = blockSize - data.length % blockSize;
    return data + String.fromCharCode(num).repeat(num);
  },

  unpad: function (data) {
    // return data;
    const dataStr = data.toString();
    console.log(typeof dataStr);
    console.log(dataStr);
    console.log(data);
    data.sigBytes -= dataStr.charCodeAt(dataStr.length - 1);
    console.log(data);
    return data;
  }
};


@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  title = 'app';

  ngOnInit() {
    // setTimeout(this.functt(), 5000)
    // this.aesDecodeTest();
    this.ecbModeTest2();
  }

  ecbModeTest() {
    const msg = 'hello world';
    const pass = 'my secret pass';
    const encr = this.encryptCBC(msg, pass);
    const decr = this.decryptCBC(encr, pass);
    console.log(decr.toString(enc.Utf8));
  }

  ecbModeTest2() {
    const data = origTxt;
    // Encrypt
    const pass = 'pass';
    let startTime = null;
    const numIterations = 1;
    let decryptedData;
    let decryptedDataStr;
    console.log('decrypting now ...');
    startTime = performance.now();
    const encryptedText = 'NQOsRF7Y4wkL4REfY3r0Si1O/kY9M754jJuNoEznchI1eRIy/LuNYakZb8YK5FJUmQ==';
    for (let i = 0; i < numIterations; i++) {
      // Decrypt
      decryptedData = this.decryptFrontendData(encryptedText, pass);
      decryptedDataStr = decryptedData.toString(enc.Utf8);
      // decryptedDataJson = JSON.parse(decryptedDataStr);
    }
    const endTime = performance.now();
    const timeTaken = (endTime - startTime) / (1000 * numIterations);
    console.log(timeTaken);
    console.log(decryptedData);
    console.log(decryptedDataStr);
  }

  aesDecodeTest() {
    const data = origTxt;
    const ciphertext = AES.encrypt(JSON.stringify(data), 'secret key 123');
    // Encrypt
    let startTime = null;
    const numIterations = 1;
    let index = 0;
    startTime = performance.now();
    for (let i = 0; i < numIterations; i++) {
      // Decrypt
      const bytes = AES.decrypt(ciphertext.toString(), 'secret key 123');
      const decryptedData = JSON.parse(bytes.toString(enc.Utf8));

    }
    const endTime = performance.now();
    const timeTaken = (endTime - startTime) / (1000 * numIterations);
    console.log(++index, timeTaken);
  }

  jwdDecodeTest() {
    const vars = [ES256, ES384, ES512, HS256, HS384, HS512, PS256, PS384, PS512, RS256, RS384, RS512];
    let startTime = null;
    const numIterations = 30;
    let index = 0;
    for (const v of vars) {
      let dec = null;
      startTime = performance.now();
      for (let i = 0; i < numIterations; i++) {
        dec = jwtDecode(v);
      }
      const endTime = performance.now();
      const timeTaken = (endTime - startTime) / (1000 * numIterations);
      console.log(++index, timeTaken);
    }
  }

  encryptCBC(msg, pass) {
    const keySize = 256;
    const iterations = 100;
    const salt = lib.WordArray.random(128 / 8);

    const key = PBKDF2(pass, salt, {
      keySize: keySize / 32,
      iterations: iterations
    });
    // const key = this.generateKey(pass, salt, 5)
    const iv = lib.WordArray.random(128 / 8);

    // console.log();
    const encrypted = AES.encrypt(msg, key, {
      iv: iv,
      padding: pad.Pkcs7,
      mode: mode.CBC
    });
    // salt, iv will be hex 32 in length
    // append them to the ciphertext for use  in decryption
    const transitmessage = salt.toString() + iv.toString() + encrypted.toString();
    return transitmessage;
  }

  decryptCBC(transitmessage, pass) {
    const keySize = 256;
    const iterations = 100;
    const salt = enc.Hex.parse(transitmessage.substr(0, 32));
    const iv = enc.Hex.parse(transitmessage.substr(32, 32));
    const encrypted = transitmessage.substring(64);

    const key = PBKDF2(pass, salt, {
      keySize: keySize / 32,
      iterations: iterations
    });

    const decrypted = AES.decrypt(encrypted, key, {
      iv: iv,
      padding: pad.Pkcs7,
      mode: mode.CBC

    });
    return decrypted;
  }

  decryptFrontendData(msg, salt) {
    console.log(enc.Base64.parse(msg).toString());


    const b64_text = atob(msg);
    console.log(b64_text);
    const BS = 16;
    const password_length = BS;
    const iv_length = BS;
    const number_of_iteration_index = password_length + iv_length;
    // ciphertext_start_index is startig index of ciphertext
    const ciphertext_start_index = password_length + iv_length + 1;

    // password is used to generate cipher_key
    const password = b64_text.slice(0, password_length);
    console.log(enc.Base64.parse(password).toString());
    // iv is used in AES decription algo
    const iv = lib.WordArray.create(b64_text.slice(password_length, password_length + iv_length));
    // console.log(lib.WordArray.create(b64_text.slice(password_length, password_length + iv_length)));

    // number_of_iteration will be used to generate cipher_key
    const number_of_iteration: number = +b64_text.slice(number_of_iteration_index, number_of_iteration_index + 1);

    // encrypted text to decipher
    const ciphertext = b64_text.slice(ciphertext_start_index);
    // const key = this.generateKey(password, salt, number_of_iteration);
    const key = PBKDF2(password, salt, {
      keySize: 16,
      iterations: number_of_iteration
    });
    // key.clamp()

    // console.log(ciphertext);
    console.log(number_of_iteration);
    const decrypted = AES.decrypt(ciphertext, key, {
      iv: iv,
      padding: pad.Pkcs7,
      mode: mode.CBC
    });
    return decrypted;
  }

  generateKey(password, salt, iterations) {
    let key = password + salt;
    for (let i = 0; i < iterations; i++) {
      key = enc.Hex.parse(SHA256(key));
    }
    console.log(key.toString());
    return key;
  }


  // var encrypted = encrypt(message, password);
  // var decrypted = decrypt(encrypted, password);
}


// PAD_TEXT = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
// UNPAD = lambda s : s[0:-ord(s[-1])]


//
// var Pkcs7 = C_pad.Pkcs7 = {
//   /**
//    * Pads data using the algorithm defined in PKCS #5/7.
//    *
//    * @param {WordArray} data The data to pad.
//    * @param {number} blockSize The multiple that the data should be padded to.
//    *
//    * @static
//    *
//    * @example
//    *
//    *     CryptoJS.pad.Pkcs7.pad(wordArray, 4);
//    */
//   pad: function (data, blockSize) {
//     // Shortcut
//     var blockSizeBytes = blockSize * 4;
//
//     // Count padding bytes
//     var nPaddingBytes = blockSizeBytes - data.sigBytes % blockSizeBytes;
//
//     // Create padding word
//     var paddingWord = (nPaddingBytes << 24) | (nPaddingBytes << 16) | (nPaddingBytes << 8) | nPaddingBytes;
//
//     // Create padding
//     var paddingWords = [];
//     for (var i = 0; i < nPaddingBytes; i += 4) {
//       paddingWords.push(paddingWord);
//     }
//     var padding = WordArray.create(paddingWords, nPaddingBytes);
//
//     // Add padding
//     data.concat(padding);
//   },
//
//   /**
//    * Unpads data that had been padded using the algorithm defined in PKCS #5/7.
//    *
//    * @param {WordArray} data The data to unpad.
//    *
//    * @static
//    *
//    * @example
//    *
//    *     CryptoJS.pad.Pkcs7.unpad(wordArray);
//    */
//   unpad: function (data) {
//     // Get number of padding bytes from last byte
//     var nPaddingBytes = data.words[(data.sigBytes - 1) >>> 2] & 0xff;
//
//     // Remove padding
//     data.sigBytes -= nPaddingBytes;
//   }
// }
