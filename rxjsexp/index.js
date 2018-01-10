// 1
// var button = document.querySelector('button');
// Rx.Observable.fromEvent(button, 'click')
// 	.throttleTime(1000)
// 	.scan(count => count + 1, 0)
// 	.subscribe(count => con)

// 2
// var button = document.querySelector('button');
// Rx.Observable.fromEvent(button, 'click')
// 	.throttleTime(1000)
// 	.map(event => event.clientX)
// 	.scan((count, clientX) => count + clientX, 0)
// 	.subscribe(count => console.log(count))

// 3
// var observable = Rx.Observable.create(function(observer){
// 	observer.next(1);
// 	observer.next(2);
// 	observer.next(3);
// 	setTimeout(() => {
// 		observer.next(4);
// 		observer.complete();
// 	}, 1000)
// });

// console.log('just before subscribe');
// observable.subscribe({
// 	next: x => console.log('got value ' + x),
// 	error: err => console.error('something wrong occurred: ' + err),
// 	complete: () => console.log('done'),

// });
// console.log('just after subscribe');




// 4
// var observable1 = Rx.Observable.interval(400);
// var observable2 = Rx.Observable.interval(300);

// var subscription = observable1.subscribe(x => console.log("first: " + x));
// var childSubscription = observable2.subscribe(x=>console.log('second: ' + x));

// subscription.add(childSubscription);
// setTimeout(() => {
//   // Unsubscribes BOTH subscription and childSubscription
//   subscription.unsubscribe();
// }, 1209);


// 5 Subject

// var subject = new Rx.Subject();

// subject.subscribe({
// 	next: (v) => console.log("Observer A: " + v)
// })


// subject.subscribe({
// 	next: (v) => console.log("Observer B: " + v)
// })

// subject.next(1);
// subject.next(2);

// 6.
// var subject = new Rx.Subject();
// subject.subscribe({
// 	next: (v) => console.log('observer A: ' + v)
// })

// subject.subscribe({
// 	next: (v) => console.log('observer B: ' + v)
// })

// var observable = Rx.Observable.from([1,2,3]);
// observable.subscribe(subject);


var clicksOrInterval = Rx.Observable.defer(function () {
  if (Math.random() > 0.5) {
    return Rx.Observable.fromEvent(document, 'click');
  } else {
    return Rx.Observable.interval(1000);
  }
});
clicksOrInterval.subscribe(x => console.log(x));





























